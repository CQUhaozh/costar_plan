export CUDA_VISIBLE_DEVICES="1" && python grasp_train.py --grasp_model grasp_model_hypertree --data_dir=~/.keras/datasets/grasping/ --grasp_success_label 'move_to_grasp/time_ordered/grasp_success' --grasp_sequence_motion_command_feature 'move_to_grasp/time_ordered/reached_pose/transforms/endeffector_current_T_endeffector_final/vec_sin_cos_5' --loss 'binary_crossentropy' --metric 'binary_accuracy' --batch_size 4
# grasp_model_levine_2016
# --grasp_model grasp_model_resnet
# --load_model '2018-01-18-02-08-57_grasp_model_weights-grasp_model_levine_2016-dataset_062_b_063_072_a_082_b_102-epoch-001-val_loss-0.775-val_acc-0.354.h5'
