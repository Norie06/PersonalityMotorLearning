# srtt_experiment_short.py
# Compact Serial Reaction Time Task (~20 min) with reward feedback every trial

from psychopy import visual, core, event, gui
import random, csv

# -----------------------------
# Participant info
# -----------------------------
exp_info = {'Participant ID': ''}
dlg = gui.DlgFromDict(dictionary=exp_info, title='SRTT Experiment')
if not dlg.OK:
    core.quit()

# -----------------------------
# Window setup
# -----------------------------
win = visual.Window(size=(800,600), color='black', units='pix')

# Stimuli positions (4 squares)
positions = [(-200,0), (-70,0), (70,0), (200,0)]
stimuli = [visual.Rect(win, width=100, height=100, pos=pos, fillColor='white') for pos in positions]

# -----------------------------
# Task parameters
# -----------------------------
n_blocks = 8           # total blocks (~20 min)
trials_per_block = 48  # trials per block
sequence = [0, 2, 3, 1, 0, 3, 2, 1, 3, 0, 1, 2]  # 12-item repeating sequence
keys = ['a','s','d','f']         # mapping to positions

# -----------------------------
# Data logging
# -----------------------------
filename = f"Data/data_{exp_info['Participant ID']}.csv"
data_file = open(filename, 'w', newline='')
writer = csv.writer(data_file)
writer.writerow(['participant','block','trial','stim_pos','correct_key','response','rt','accuracy','score'])

# -----------------------------
# Trial function
# -----------------------------
def run_trial(block, trial, stim_index, score, log_data=True, is_practice=False):
    # quit check
    if 'escape' in event.getKeys():
        data_file.close()
        win.close()
        core.quit()

    # highlight stimulus
    for stim in stimuli:
        stim.fillColor = 'white'
    stimuli[stim_index].fillColor = 'red'
    for stim in stimuli:
        stim.draw()
    
    # display score in top-right corner
    score_display = visual.TextStim(win, text=f"Score: {score}", color='white', height=25, pos=(300, 250))
    score_display.draw()
    win.flip()

    # collect response
    clock = core.Clock()
    keys_pressed = event.waitKeys(keyList=keys, timeStamped=clock)
    response, rt = keys_pressed[0]

    # accuracy
    correct_key = keys[stim_index]
    accuracy = int(response == correct_key)

    # update score: base points for accuracy + bonus for speed (only if not practice)
    points_awarded = 0
    if accuracy == 1 and not is_practice:
        # 10 points for correct + speed bonus (faster = more points)
        # bonus: 1 point per 100ms under 1 second (max 10 bonus points at 0.1s or faster)
        speed_bonus = max(0, int((1.0 - rt) * 10))
        points_awarded = 10 + speed_bonus
        score += points_awarded
    else:
        # 0 points for incorrect or practice
        points_awarded = 0

    # log only if this is a real trial (not practice)
    if log_data:
        writer.writerow([exp_info['Participant ID'], block, trial, stim_index,
                         correct_key, response, rt, accuracy, score])

    # brief feedback: show correctness indicator (checkmark or x)
    feedback_color = 'green' if accuracy == 1 else 'red'
    feedback_text = '✓' if accuracy == 1 else '✗'
    
    # display just the symbol
    feedback = visual.TextStim(win, text=feedback_text, color=feedback_color, height=80, pos=(0, 150))
    
    # draw feedback with stimuli (flashed briefly)
    for stim in stimuli:
        stim.fillColor = 'white'
    for stim in stimuli:
        stim.draw()
    feedback.draw()
    win.flip()
    core.wait(0.10)  # brief feedback flash
    
    # show pressed button darker before next trial
    # pressed button is identified by the response key, not the stimulus index
    response_index = keys.index(response)
    
    # if correct: button was red, so turn darker red; if incorrect: button was white, so turn darker gray
    for i, stim in enumerate(stimuli):
        if i == response_index:
            if accuracy == 1:
                stim.fillColor = 'darkred'     # correct: was red, now darker red
            else:
                stim.fillColor = 'darkgray'    # incorrect: was white, now darker gray
        else:
            stim.fillColor = 'white'
    for stim in stimuli:
        stim.draw()
    win.flip()
    core.wait(0.05)  # very brief visual feedback of press

    return score

# -----------------------------
# Starting screen
# -----------------------------
start_text = visual.TextStim(win, text="Serial Reaction Time Task\n\nYour goal: React as fast and accurately as possible to the red squares.\n\nPress SPACE to begin.", color='white', height=30)
start_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Initialize score
score = 0

# Practice block - random sequence
practice_text = visual.TextStim(win, text="Let's practice!\n\nReact to the red squares. This is a practice round.\n\nPress SPACE to start.", color='white', height=28)
practice_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

practice_stim_order = [random.choice(range(4)) for _ in range(8)]  # 8 short practice trials
for trial, stim_index in enumerate(practice_stim_order, start=1):
    run_trial(0, trial, stim_index, score, log_data=False, is_practice=True)  # is_practice=True: no points awarded

# End of practice
practice_end_text = visual.TextStim(win, text="Practice complete!\n\nNow the real task begins.\n\nPress SPACE to continue.", color='white', height=28)
practice_end_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Experiment loop
for block in range(1, n_blocks+1):
    # block design: 1 baseline random, 4 sequence, 2 random, 1 transfer
    if block == 1:
        stim_order = [random.choice(range(4)) for _ in range(trials_per_block)]
    elif block in [2,3,4,5]:
        stim_order = sequence * (trials_per_block // len(sequence))
    elif block in [6,7]:
        stim_order = [random.choice(range(4)) for _ in range(trials_per_block)]
    else:  # transfer block (new random sequence)
        new_seq = [3,2,0,1,2,0,3,0,2,1,3,0]
        stim_order = new_seq * (trials_per_block // len(new_seq))

    # run block
    block_start_score = score
    for trial, stim_index in enumerate(stim_order, start=1):
        score = run_trial(block, trial, stim_index, score)
    block_end_score = score
    block_points = block_end_score - block_start_score

    # short break with block score and total score display
    block_score_text = f"End of block {block}\n\nBlock Score: {block_points} points\nTotal Score: {score} points\n\nPress space to continue."
    msg = visual.TextStim(win, text=block_score_text, color='white', height=28)
    msg.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

# -----------------------------
# Awareness check
# -----------------------------
msg = visual.TextStim(win, text="Did you notice a repeating pattern? (y/n)", color='white')
msg.draw()
win.flip()
keys_pressed = event.waitKeys(keyList=['y','n'])
awareness = keys_pressed[0]

writer.writerow([exp_info['Participant ID'],'awareness','','','','',awareness,'',''])

msg = visual.TextStim(win, text="Try to type the sequence you think repeated (keys a/s/d/f). Press Enter when done.", color='white')
msg.draw()
win.flip()

# collect key presses until 'return' is pressed
typed_seq = []
while True:
    keys_pressed = event.waitKeys(keyList=keys+['return'])
    for key in keys_pressed:
        if key == 'return':
            break
        else:
            typed_seq.append(key)
    if 'return' in keys_pressed:
        break

# log typed sequence (joined string)
typed_str = ''.join(typed_seq)
writer.writerow([exp_info['Participant ID'],'awareness_guess','','','','',typed_str,'',''])

# -----------------------------
# End
# -----------------------------
msg = visual.TextStim(win, text="Thank you for participating!", color='white')
msg.draw()
win.flip()
event.waitKeys()
data_file.close()
win.close()
core.quit()