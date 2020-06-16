from full_aircraft import *
import os
from Function.help_fucntions import *
from parapy.core.decorators import action


class Main(Base):
    input = ReadGeometry("A320")
    
    ct_chord_root_ratio = Input(0.4)  # chord_winglet_root / chord_wingtip
    ct_height_ratio = Input(0.1)
    ct_taper_ratio = Input(0.2)
    ct_sweep = Input(30)
    ct_cant = Input(0)
    ct_toe = Input(-5)
    ct_twist_tip = Input(-6)

    TYPE_winglet = Input(0)
    chord_root_ratio_step = Input(0.2)
    height_ratio_step = Input(0.1)
    taper_ratio_step = Input(0.1)
    sweep_step = Input(20)
    cant_step = Input(10)
    toe_step = Input(5)
    twist_tip_step = Input(6)

    var_1 = Input("ct_taper_ratio", validator=is_string)
    var_2 = Input("ct_toe", validator=is_string)
    var_3 = Input("ct_twist_tip", validator=is_string)

    @Attribute
    def input_list(self):
        return ['ct_chord_root_ratio', 'ct_height_ratio', 'ct_taper_ratio',
                'ct_sweep', 'ct_cant', 'ct_toe', 'ct_twist_tip']

    @Attribute
    def initval_list(self):
        return [self.ct_chord_root_ratio, self.ct_height_ratio, self.ct_taper_ratio,
                self.ct_sweep, self.ct_cant, self.ct_toe, self.ct_twist_tip]

    @Attribute
    def step_list(self):
        return [self.chord_root_ratio_step, self.height_ratio_step, self.taper_ratio_step,
                self.sweep_step, self.cant_step, self.toe_step, self.twist_tip_step]

    @Attribute
    def var2evaluate(self):
        flag = 0
        for i, selection in enumerate(self.input_list):
            if self.var_1 == selection:
                var1 = self.input_list[i]
                var1_value = self.initval_list[i]
                var1_num = i
                flag = flag + 1
            if self.var_2 == selection:
                var2 = self.input_list[i]
                var2_value = self.initval_list[i]
                var2_num = i
                flag = flag + 1
            if self.var_3 == selection:
                var3 = self.input_list[i]
                var3_value = self.initval_list[i]
                var3_num = i
                flag = flag + 1
        # check if the input names are correct
        if flag != 3:
            generate_warning(' ', 'Input error')
        to_return = [[var1, var1_value, var1_num], [var2, var2_value, var2_num], [var3, var3_value, var3_num]]
        return to_return

    @action(label='Reset')
    def reset(self):
        try:
            os.remove(self.path_iter_output)
        except FileNotFoundError:
            pass
        with open(self.path_iter_output, 'w+') as f:
            f.write(str(self.var_1) + '\t' + str(self.var_2) + '\t' + str(self.var_3) + '\t' +
                    'CL' + '\t' + 'CD' + '\t' + 'l_over_d' + '\n')

    @Attribute
    def find_best(self):
        iterator = 0
        var1 = self.var2evaluate[0][0]
        var1_ = self.var2evaluate[0][1]
        var1_num = self.var2evaluate[0][2]
        var2 = self.var2evaluate[1][0]
        var2_ = self.var2evaluate[1][1]
        var2_num = self.var2evaluate[1][2]
        var3 = self.var2evaluate[2][0]
        var3_ = self.var2evaluate[2][1]
        var3_num = self.var2evaluate[2][2]

        var1_raw = var1_
        var2_raw = var2_
        var3_raw = var3_

        aircraft = Aircraft(TYPE_winglet=0,
                            ct_chord_root_ratio=self.initval_list[0],
                            ct_height_ratio=self.initval_list[1],
                            ct_taper_ratio=self.initval_list[2],
                            ct_sweep=self.initval_list[3],
                            ct_cant=self.initval_list[4],
                            ct_toe=self.initval_list[5],
                            ct_twist_tip=self.initval_list[6])
        limit_list = aircraft.right_winglet.limit_list
        last_input_list = self.initval_list

        while var1_ <= float(limit_list[var1_num][1]):
            if aircraft.right_winglet.percent_span_increase > aircraft.right_winglet.limit_span_increase:
                break
            else:
                while var2_ <= float(limit_list[var2_num][1]):
                    if aircraft.right_winglet.percent_span_increase > aircraft.right_winglet.limit_span_increase:
                        break
                    else:
                        while var3_ <= float(limit_list[var3_num][1]):
                            if aircraft.right_winglet.percent_span_increase > aircraft.right_winglet.limit_span_increase:
                                break
                            else:
                                new_input_list = last_input_list
                                new_input_list[var3_num] = var3_
                                aircraft = Aircraft(TYPE_winglet=0,
                                                    ct_chord_root_ratio=new_input_list[0],
                                                    ct_height_ratio=new_input_list[1],
                                                    ct_taper_ratio=new_input_list[2],
                                                    ct_sweep=new_input_list[3],
                                                    ct_cant=new_input_list[4],
                                                    ct_toe=new_input_list[5],
                                                    ct_twist_tip=new_input_list[6])

                                CL = aircraft.avl_analysis.CL
                                CD = aircraft.avl_analysis.CD
                                l_over_d = aircraft.avl_analysis.l_over_d
                                self.write_file(var1_, var2_, var3_, CL, CD, l_over_d)
                                var3_ = var3_ + self.step_list[var3_num]
                                iterator = iterator + 1
                        var2_ = var2_ + self.step_list[var2_num]
                        var3_ = var3_raw
                        last_input_list[var3_num] = var3_raw
                        last_input_list[var2_num] = var2_
                var1_ = var1_ + self.step_list[var1_num]
                var2_ = var2_raw
                last_input_list[var2_num] = var2_raw
                last_input_list[var1_num] = var1_
        msg = 'Iteration finished'
        generate_warning(' ', msg)

        l_over_d_max = 0
        with open(self.path_iter_output, 'r') as f:
            data = f.readlines()
            nu_lines = len(data)
            data = data[1:nu_lines]
            for i in range(0, len(data)):
                data[i] = data[i].split('\t')
                nu_data = len(data[i])
                data[i][nu_data - 1] = data[i][nu_data - 1].strip()
                l_over_d = float(data[i][nu_data - 1])
                if l_over_d > l_over_d_max:
                    l_over_d_max = l_over_d
                    which_row = i
            best_var1 = round(float(data[which_row][0]), 2)
            best_var2 = round(float(data[which_row][1]), 2)
            best_var3 = round(float(data[which_row][2]), 2)
        best_input_list = self.initval_list
        best_input_list[var1_num] = best_var1
        best_input_list[var2_num] = best_var2
        best_input_list[var3_num] = best_var3
        print(best_input_list)
        return best_input_list

    # @Attribute
    # def adjust_shape(self):
    #     # CD = []
    #     # l_over_d = []
    #     # ct_cant = []
    #     # ct_toe = []
    #     # ct_twist_tip = []
    #     iterator = 0
    #     ct_cant = self.ct_cant
    #     ct_toe = self.ct_toe
    #     ct_twist_tip = self.ct_twist_tip
    #     aircraft = Aircraft(TYPE_winglet=self.TYPE_winglet,
    #                         ct_cant=self.ct_cant,
    #                         ct_twist_tip=self.ct_twist_tip,
    #                         ct_toe=self.ct_toe)
    #
    #     CL = aircraft.avl_analysis.CL
    #     CD = aircraft.avl_analysis.CD
    #     l_over_d = aircraft.avl_analysis.l_over_d
    #     self.write_file(ct_cant, ct_twist_tip, ct_toe, CL, CD, l_over_d)
    #
    #     while ct_cant < float(aircraft.right_winglet.cant_limit[1]):
    #         if aircraft.right_winglet.percent_span_increase > aircraft.right_winglet.limit_span_increase:
    #             break
    #         else:
    #             while ct_toe < float(aircraft.right_winglet.toe_limit[1]):
    #                 if aircraft.right_winglet.percent_span_increase > aircraft.right_winglet.limit_span_increase:
    #                     break
    #                 else:
    #                     while ct_twist_tip < float(aircraft.right_winglet.twist_tip_tip_limit[1]):
    #                         if aircraft.right_winglet.percent_span_increase > aircraft.right_winglet.limit_span_increase:
    #                             break
    #                         else:
    #                             ct_twist_tip = ct_twist_tip + self.twist_tip_step
    #                             aircraft = Aircraft(TYPE_winglet=self.TYPE_winglet,
    #                                                 ct_cant=ct_cant,
    #                                                 ct_toe=ct_toe,
    #                                                 ct_twist_tip=ct_twist_tip)
    #                             CL = aircraft.avl_analysis.CL
    #                             CD = aircraft.avl_analysis.CD
    #                             l_over_d = aircraft.avl_analysis.l_over_d
    #                             self.write_file(ct_cant, ct_twist_tip, ct_toe, CL, CD, l_over_d)
    #                             iterator = iterator + 1
    #                     ct_twist_tip = self.ct_twist_tip
    #                     ct_toe = ct_toe + self.toe_step
    #             ct_toe = self.ct_toe
    #             ct_cant = ct_cant + self.cant_step
    #     msg = 'Iteration finished'
    #     generate_warning(' ', msg)
    #     return iterator, ct_cant, ct_twist_tip, ct_toe

    @Attribute
    def path_iter_output(self):
        path_wd = os.getcwd()
        path_iter_output = path_wd + '\\Output\\iterator_output.txt'
        return path_iter_output

    @Attribute
    def best_inputs(self):
        best_inputs = self.find_best
        return best_inputs

    @Part
    def aircraft_origin(self):
        return Aircraft(color='red')

    @Part
    def aircraft_best(self):
        return Aircraft(TYPE_winglet=0,
                        ct_chord_root_ratio=self.best_inputs[0],
                        ct_height_ratio=self.best_inputs[1],
                        ct_taper_ratio=self.best_inputs[2],
                        ct_sweep=self.best_inputs[3],
                        ct_cant=self.best_inputs[4],
                        ct_toe=self.best_inputs[5],
                        ct_twist_tip=self.best_inputs[6])

    def write_file(self, var1, var2, var3, CL, CD, l_over_d):
        with open(self.path_iter_output, 'a+') as f:
            f.write(str(round(var1, 2)) + '\t' + str(round(var2, 2)) + '\t' + str(round(var3, 2)) + '\t' +
                    str(CL) + '\t' + str(CD) + '\t' + str(l_over_d) + '\n')


if __name__ == '__main__':
    from parapy.gui import display
    obj = Main()
    display(obj)
