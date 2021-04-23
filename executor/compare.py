"""
Run symbolic reasoning on multiple-choice questions
"""
import os
import sys
import json
import argparse

from executor import Executor
from simulation import Simulation


parser = argparse.ArgumentParser()
parser.add_argument('--n_progs', required=True)
parser.add_argument('--use_event_ann', default=1, type=int)
parser.add_argument('--use_in', default=0, type=int)  # Use interaction network
args = parser.parse_args()


my_motion_dir = 'data/propnet_preds/with_edge_supervision'
raw_motion_dir = 'data/propnet_preds/with_edge_supervision_bak'



question_path = 'data/validation.json'
if args.n_progs == 'all':
    program_path = 'data/parsed_programs/mc_allq_allc.json'
else:
    program_path = 'data/parsed_programs/mc_{}q_{}c_val_new.json'.format(args.n_progs, int(args.n_progs)*4)

oe_program_path = 'data/parsed_programs/oe_{}pg_val_new.json'.format(args.n_progs)

with open(program_path) as f:
    parsed_pgs = json.load(f)
with open(oe_program_path) as f:
    oe_parsed_pgs = json.load(f)
with open(question_path) as f:
    anns = json.load(f)

total, correct = 0, 0
total_per_q, correct_per_q = 0, 0
total_expl, correct_expl = 0, 0
total_expl_per_q, correct_expl_per_q = 0, 0
total_pred, correct_pred = 0, 0
total_pred_per_q, correct_pred_per_q = 0, 0
total_coun, correct_coun = 0, 0
total_coun_per_q, correct_coun_per_q = 0, 0
total_desc, correct_desc = 0, 0

pred_map = {'yes': 'correct', 'no': 'wrong', 'error': 'error'}
for ann_idx in range(0, 5000):
    if ann_idx % 100 == 0:
        print(ann_idx)
    question_scene = anns[ann_idx]
    file_idx = ann_idx + 10000
    ann_path = os.path.join(raw_motion_dir, 'sim_%05d.json' % file_idx)
    my_ann_path = os.path.join(my_motion_dir, 'sim_%05d.json' % file_idx)

    sim = Simulation(ann_path, use_event_ann=(args.use_event_ann != 0))
    mysim = Simulation(my_ann_path, use_event_ann=(args.use_event_ann != 0))
    exe = Executor(sim)
    myexe = Executor(mysim)
    valid_q_idx = 0
    for q_idx, q in enumerate(question_scene['questions']):
        question = q['question']
        q_type = q['question_type']
        if q_type == 'descriptive':
            question = q['question']
            parsed_pg = oe_parsed_pgs[str(file_idx)]['questions'][q_idx]['program']
            pred = exe.run(parsed_pg, debug=False)
            mypred = myexe.run(parsed_pg, debug=False)
            ans = q['answer']
            # if open(ann_path).read() != open(my_ann_path).read():
            #     pred = ans
            #     print(parsed_pg, mysim.in_out, sim.in_out)

            # if ans == mypred and pred != mypred:
            #     print('GOOD_' + q['question_type'], ann_idx, q_idx, question, ans, pred, mypred)
            # if ans == pred and pred != mypred:
            #     print('BAD_' + q['question_type'], ann_idx, q_idx, question, ans, pred, mypred)
            if pred == ans:
                correct_desc += 1
                correct += 1
                correct_per_q += 1
            total_desc += 1
            total += 1
            total_per_q += 1
            continue

        q_ann = parsed_pgs[str(file_idx)]['questions'][valid_q_idx]
        correct_question = True
        for c_idx, c in enumerate(q_ann['choices']):
            full_pg = c['program'] + q_ann['question_program']
            ans = c['answer']
            pred = exe.run(full_pg, debug=False)
            mypred = myexe.run(full_pg, debug=False)
            pred = pred_map[pred]
            mypred = pred_map[mypred]
            # if open(ann_path).read() != open(my_ann_path).read():
            #     pred = ans

            # if ans == mypred and pred != mypred:
            #     print('GOOD_' + q['question_type'], ann_idx, q_idx, c_idx, question, c['program'], ans, pred, mypred)
            # if ans == pred and pred != mypred:
            #     print('BAD_' + q['question_type'], ann_idx, q_idx, c_idx, question, c['program'], ans, pred, mypred)
            if ans == pred:
                correct += 1
            else:
                correct_question = False
            total += 1

            if q['question_type'].startswith('explanatory'):
                if ans == pred:
                    correct_expl += 1
                total_expl += 1

            if q['question_type'].startswith('predictive'):
                # print(pred, ans)
                if ans == pred:
                    correct_pred += 1
                total_pred += 1

            if q['question_type'].startswith('counterfactual'):
                if ans == pred:
                    correct_coun += 1
                total_coun += 1

        if correct_question:
            correct_per_q += 1
        total_per_q += 1

        if q['question_type'].startswith('explanatory'):
            if correct_question:
                correct_expl_per_q += 1
            total_expl_per_q += 1

        if q['question_type'].startswith('predictive'):
            if correct_question:
                correct_pred_per_q += 1
            total_pred_per_q += 1

        if q['question_type'].startswith('counterfactual'):
            if correct_question:
                correct_coun_per_q += 1
            total_coun_per_q += 1
        valid_q_idx += 1
    # pbar.set_description('per choice {:f}, per questions {:f}'.format(float(correct)*100/total, float(correct_per_q)*100/total_per_q))

print('============ results ============')
print('overall accuracy per option: %f %%' % (float(correct) * 100.0 / total))
print('overall accuracy per question: %f %%' % (float(correct_per_q) * 100.0 / total_per_q))
print('descriptive accuracy per question: %f %%' % (float(correct_desc) * 100.0 / total_desc))
print('explanatory accuracy per option: %f %%' % (float(correct_expl) * 100.0 / total_expl))
print('explanatory accuracy per question: %f %%' % (float(correct_expl_per_q) * 100.0 / total_expl_per_q))
print('predictive accuracy per option: %f %%' % (float(correct_pred) * 100.0 / total_pred))
print('predictive accuracy per question: %f %%' % (float(correct_pred_per_q) * 100.0 / total_pred_per_q))
print('counterfactual accuracy per option: %f %%' % (float(correct_coun) * 100.0 / total_coun))
print('counterfactual accuracy per question: %f %%' % (float(correct_coun_per_q) * 100.0 / total_coun_per_q))
print('============ results ============')

output_ann = {
    'total_options': total,
    'correct_options': correct,
    'total_questions': total_per_q,
    'correct_questions': correct_per_q,
    'total_descriptive_options': total_desc,
    'correct_descriptive_options': correct_desc,
    'total_explanatory_options': total_expl,
    'correct_explanatory_options': correct_expl,
    'total_explanatory_questions': total_expl_per_q,
    'correct_explanatory_questions': correct_expl_per_q,
    'total_predictive_options': total_pred,
    'correct_predictive_options': correct_pred,
    'total_predictive_questions': total_pred_per_q,
    'correct_predictive_questions': correct_pred_per_q,
    'total_counterfactual_options': total_coun,
    'correct_counterfactual_options': correct_coun,
    'total_counterfactual_questions': total_coun_per_q,
    'correct_counterfactual_questions': correct_coun_per_q,
}

output_file = 'result.json'
if args.use_in != 0:
    output_file = 'result_in.json'
with open(output_file, 'w') as fout:
    json.dump(output_ann, fout)
