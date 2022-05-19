from gvlab.send_gvlab_tasks import mturk


def main():
    all_creators = {'A377LTGWJKY2IW', 'A3RTW9UWYKSNWX', 'A2M3C5YIO7IZ6G', 'A16184N1RO5OJV', 'AHB3QFZSFN9DL', 'A2ONILC0LZKG6Y', 'A2UCKZZI9KBBCV', 'A2K607J3Z68WRR', 'A3UJSDFJ9LBQ6Z', 'A302KOFOYLD89A', 'A2QX3YJXAAHHVV', 'A382S0KJMW3K9S', 'AKQAI78JTXXC9', 'A1PBRKFHSF1OF8', 'A2V3P1XE33NYC3', 'AZLZA0Q87TJZO', 'A1OZPLHNIU1519', 'A19UED74G8FXN3', 'A1HKYY6XI2OHO1', 'A2SDOD67560IN8', 'A2N9U74YIPDQ9F'}  # added carbo - new one
    revoked_creators = {'AKQAI78JTXXC9', 'A2UCKZZI9KBBCV'}  # A1HKYY6XI2OHO1 - good enough
    creators_not_revoked = all_creators.difference(revoked_creators)
    # Subject = "50% increased bonus for high fool-the-AI scores, 'create' qualification revoke risk for low fool-the-AI score"
    # Message = "Hello. We aim to collect data that is challenging for the AI. We take additional two steps towards this goal:' \
    #           '\n (1) 50% increased bonus for high fool-the-AI scores (while still solvable-by-humans). ' \
    #           '\n If 67 <= fool-the-ai < 80, the bonus will be 0.18$ (instead of 0.12$).' \
    #           '\n If 80 <= fool-the-ai, the bonus will be 0.27$ (instead of 0.18$).' \
    #           '\n (2) If your fool-the-AI score average over 50 associations is lower than 30%, your 'create' qualification may be revoked' \
    #           '\n Thanks and have fun :)"
    subject = "GVLAB: New test 'create' HITs are available"
    message = 'Hello. A new "create" batch is available: "GVLAB: Visual Associations - Create (create_random items 0-100)". Please say if you notice something *different* in this batch from the previous batches.'
    print(subject)
    print(message)
        # Subject = 'GVLAB Creators: Getting ready for the next batch, here are some great examples you created! Waiting for your approval.'
    # SubjectNewBatch = "GVLAB Creators: New batch is available with increased pay :) Please read previous mail before solving"
    # MessageNewBatch = "Please don't solve the new batch until reading the previous mail and seeing the good examples. " \
    #                   "\n Help us to pay you more :) Try to achieve better 'fool-the-AI' score and maintaining 80% 'solvable-by-humans' score."
    # Message = "Hello, here are some great examples you (the group) created in the first 0-100 batch. " \
    #                         "Link: https://docs.google.com/presentation/d/1iRm_ANkPbgHGq9UZi2944Xzt16ObInE5/edit' \
    #                         '\n In all of these examples, the 'solvable-by-humans' score is 100% - meaning that it was solved perfectly by 5 different human solvers," \
    #                         "\n And the 'fool-the-AI' score was above 80%! (model performance <=20%)." \
    #                         "\n The total reward for each of such association is 0.23$!" \
    #                         "\n Try to learn and understand how to create such examples. " \
    #                         "\n We have a mutual interest: the bigger the 'fool-the-AI' score, and as long 'solvable-by-humans' score is at least 80%, the higher the rewards ($$$) you receive, and the better data we collect." \
    #                         "\n It'd be great if you respond that you read & understand this mail. " \
    #                         "\n Stay tuned for the next batch (in a few hours, waiting for your responsees)." \
    #                         "\n Please reach out if you have any questions or feedback."
    # print(Message)
    # response = mturk.notify_workers(Subject=Subject, MessageText=Message,
    #                                 WorkerIds=list(all_creators))  # response['NotifyWorkersFailureStatuses']
    response = mturk.notify_workers(Subject=subject, MessageText=message,
                                    WorkerIds=list(creators_not_revoked))  # response['NotifyWorkersFailureStatuses']
    print(response)
    print("Done")

if __name__ == '__main__':
    main()