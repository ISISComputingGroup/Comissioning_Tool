from tkinter import StringVar, ttk, messagebox, E, W, DISABLED, NORMAL

lim_repr = lambda lim: "Unknown" if lim is None else lim


class MotorSettings(ttk.Frame):
    SOFT_LABEL = "Soft"
    HARD_LABEL = "Hard"

    # Bound controls stored as control: attribute
    axis_bound_controls = dict()

    def __init__(self, axis, parent, par_change_axis):
        ttk.Frame.__init__(self, parent, padding="10")
        self.axis = axis

        self.chosen_axis = StringVar(value=self.axis.axis_letter)

        self.calc_steps = StringVar(value="0.0")
        self.calc_steps.trace("w", lambda *args: self.do_calculation(mot_steps=self.calc_steps.get()))
        self.calc_cnts = StringVar(value="0.0")
        self.calc_cnts.trace("w", lambda *args: self.do_calculation(enc_cnts=self.calc_cnts.get()))
        self.calc_pos = StringVar(value="0.0")
        self.calc_pos.trace("w", lambda *args: self.do_calculation(pos=self.calc_pos.get()))

        self.create_widgets()
        self.bind_axis(axis)

        self.chosen_axis.trace("w", lambda *args: par_change_axis(self.chosen_axis.get()))

    def do_calculation(self, **vals):
        for k, v in vals.iteritems():
            try:
                vals[k] = float(v)
            except:
                return

        if "enc_cnts" in vals:
            stps_per_cnt = self.axis.microstep.get()/(self.axis.motor_res.get()*self.axis.enc_res.get())
            self.calc_steps.set(vals["enc_cnts"]*stps_per_cnt)
        elif "mot_steps" in vals:
            self.calc_pos.set(vals["mot_steps"]*self.axis.motor_res.get()/self.axis.microstep.get())
        elif "pos" in vals:
            self.calc_cnts.set(vals["pos"]*self.axis.enc_res.get())

    def bind_axis(self, new_axis):
        self.axis = new_axis
        for con, bind in self.axis_bound_controls.items():
            con["textvariable"] = getattr(self.axis, bind)
        self.axis.limits_found.trace("w", self._update_lims)
        self._update_lims()
        self._set_soft_limits()

    def _update_lims(self, *args):
        state = NORMAL if self.axis.limits_found.get() else DISABLED
        self.set_lims.configure(state=state)
        self.limits_grid.set(self.HARD_LABEL, column=0, value=lim_repr(self.axis.low_limit))
        self.limits_grid.set(self.HARD_LABEL, column=1, value=lim_repr(self.axis.high_limit))

    def _set_soft_limits(self):
        self.axis.set_soft_limits()
        self.limits_grid.set(self.SOFT_LABEL, column=0, value=lim_repr(self.axis.get_soft_limit(False)))
        self.limits_grid.set(self.SOFT_LABEL, column=1, value=lim_repr(self.axis.get_soft_limit(True)))

    def jog_axis(self, forwards):
        msg = "The motor has not yet been setup. This means the limits could be wrong and cause a crash."
        msg += " Continue anyway?"
        if self.axis.limits_found.get() or messagebox.askyesno("Motor Not Setup", msg):
            self.axis.jog(forwards)

    def _create_bound_entry(self, col, row, attr, parent=None, **opts):
        e = ttk.Entry(self) if parent is None else ttk.Entry(parent)
        for k, v in opts.items():
            e[k] = v
        e.grid(column=col, row=row)
        self.axis_bound_controls[e] = attr
        return e

    def create_widgets(self):
        available_axes = list(map(chr, range(ord('A'), ord('H')+1)))

        ttk.Style().configure("head.TMenubutton", font="Times 20")
        ttk.Label(self, text="Axis under test: ", font="Times 20").grid(column=0, row=0, columnspan=2, pady="10", sticky=E)
        axes = ttk.OptionMenu(self, self.chosen_axis, self.axis.axis_letter, *available_axes, style="head.TMenubutton")
        axes.grid(column=2, row=0, sticky=W)

        ttk.Label(self, text="Speed (steps/s): ").grid(column=0, row=1)
        self._create_bound_entry(1, 1, "JOG_SPEED")

        ttk.Button(self, text="Jog Forward", command=lambda: self.jog_axis(True)).grid(column=2, row=1)
        ttk.Button(self, text="Jog Backward", command=lambda: self.jog_axis(False)).grid(column=3, row=1)

        ttk.Label(self, text="Soft Limit Offset (steps): ").grid(column=0, row=2)
        self._create_bound_entry(1, 2, "offset")

        self.set_lims = ttk.Button(self, text="Set Limits", state=DISABLED, command=self._set_soft_limits)
        self.set_lims.grid(column=2, row=2)

        self.limits_grid = ttk.Treeview(self, columns=("Lower Limit", "Upper Limit"), height=3)
        self.limits_grid.heading('#0', text="Limit Type")
        self.limits_grid.heading('#1', text="Lower Limit (steps)")
        self.limits_grid.heading('#2', text="Upper Limit (steps)")
        self.limits_grid.insert('', 0, iid=self.HARD_LABEL, text=self.HARD_LABEL)
        self.limits_grid.insert('', 1, iid=self.SOFT_LABEL, text=self.SOFT_LABEL)
        self.limits_grid.grid(column=0, row=3, columnspan=4, padx="40", pady="10")

        ttk.Label(self, text="Motor Type: ").grid(column=0, row=4)
        self._create_bound_entry(1, 4, "motor_type", state=DISABLED)

        ttk.Label(self, text="Encoder Type: ").grid(column=2, row=4)
        self._create_bound_entry(3, 4, "encoder_type", state=DISABLED)

        res = ttk.LabelFrame(self, text="Resolution Settings", padding=5)
        res.grid(column=0, columnspan=4, row=5, pady=10)

        motor_res_text = "Motor Resolution ({}m/full step):".format(chr(181))
        ttk.Label(res, text=motor_res_text).grid(column=0, row=0, pady=5, padx=5)
        self._create_bound_entry(1, 0, "motor_res", res)

        ttk.Label(res, text="Microstepping (steps/full step):").grid(column=2, row=0, padx=5)
        self._create_bound_entry(3, 0, "microstep", res)

        ttk.Label(res, text="Encoder Resolution (counts/"+chr(181)+"m)").grid(column=0, row=1, padx=5)
        self._create_bound_entry(1, 1, "enc_res", res)

        calc = ttk.LabelFrame(self, text="Calculator", padding=5)
        calc.grid(column=0, columnspan=4, row=6)

        ttk.Label(calc, text="Motor Steps:").grid(column=0, row=0, pady=5)
        ttk.Entry(calc, textvariable=self.calc_steps).grid(column=1, row=0, padx=5)
        ttk.Label(calc, text="Encoder Counts:").grid(column=2, row=0)
        ttk.Entry(calc, textvariable=self.calc_cnts).grid(column=3, row=0, padx=5)
        ttk.Label(calc, text="Microns:").grid(column=4, row=0)
        ttk.Entry(calc, textvariable=self.calc_pos).grid(column=5, row=0, padx=5)


