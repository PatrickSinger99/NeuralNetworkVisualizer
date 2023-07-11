import random
import tkinter as tk
from tkinter.font import Font


class App(tk.Tk):
    def __init__(self, *args):
        super().__init__()

        self.resizable(False, False)
        self.title("Neural Network Graph")

        """COLORS"""

        self.neuron_hover_color = "orange"
        self.neuron_normal_color = "white"
        self.connection_normal_color = "black"
        self.connection_background_color = "light grey"
        self.input_layer_bg = "#DEEDDC"
        self.output_layer_bg = "#EADADA"
        self.hidden_layer_alternating_bgs = ["white", "#F4F4F4"]

        """DIMENSIONS/SCALES"""

        # Constant
        self.canvas_height = 500
        self.max_canvas_width = 1000
        self.neuron_x_padding = 40
        self.neuron_y_padding = 40
        self.base_layer_gap = 150

        # Variable based on input
        self.neuron_size = 30
        self.neuron_gap = 5
        self.layer_gap = self.base_layer_gap  # Can change if more layers are given than can fit with max_canvas_width

        """CANVAS FRAME"""

        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(side="right")

        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=self.canvas_height, borderwidth=0,
                                highlightthickness=0)
        self.canvas.pack()

        """INITIALIZATIONS"""

        self.layer_neuron_elements = []  # Contains one list per layer containing the canvas elements of the neurons
        self.connection_elements = {}  # Contains canvas connection elements. Key = (layer, start neuron, end neuron)
        self.connection_colors = {}
        self.layer_bgs = []
        self.draw_fully_connected(args)

        for l, s, e in self.connection_elements:
            self.change_connection_weight_value(l, s, e, weight=1)

        self.draw_layers(args)

    def draw_fully_connected(self, *args):
        if type(args[0]) in (list, tuple):
            args = args[0]

        # Determine neuron size based on max amount of neurons per layer
        self.neuron_size = ((self.canvas_height - self.neuron_gap*(max(args)-1)) - 2*self.neuron_y_padding) / max(args)

        # Determine canvas size
        new_canvas_width = (len(args) - 1) * self.base_layer_gap + 2 * self.neuron_x_padding + self.neuron_size
        if new_canvas_width > self.max_canvas_width:
            self.layer_gap = (self.max_canvas_width - 2 * self.neuron_x_padding - self.neuron_size) / (len(args) - 1)
            self.canvas["width"] = self.max_canvas_width

        else:
            self.canvas["width"] = new_canvas_width
            self.layer_gap = 150

        # Reset the canvas elements lists
        self.layer_neuron_elements = []
        self.connection_elements = {}
        self.connection_colors = {}
        self.layer_bgs = []
        self.canvas.delete('all')

        for i, neuron_num in enumerate(args):
            neuron_elements = self.draw_layer(i+1, neuron_num)
            self.layer_neuron_elements.append(neuron_elements)

        self.draw_connections()

    def draw_connections(self, connection_weights=None):
        # Create a list with identical structure to self.layer_neuron_elements containing the center for each neuron
        neuron_centers = []
        for layer in self.layer_neuron_elements:
            layer_list = []
            for neuron in layer:
                coords = self.canvas.coords(neuron)
                layer_list.append([coords[0] + self.neuron_size / 2, coords[1] + self.neuron_size / 2])
            neuron_centers.append(layer_list)

        # Draw every connection
        for layer_index, layer in enumerate(neuron_centers[:-1]):
            for start_index, neuron_coord in enumerate(layer):
                for end_index, end_neuron_coord in enumerate(neuron_centers[layer_index+1]):
                    new_line = self.canvas.create_line(neuron_coord, end_neuron_coord,
                                                       fill=self.connection_normal_color)
                    self.canvas.lower(new_line)  # Send connection line to back
                    self.connection_elements[layer_index, start_index, end_index] = new_line

                    # Optional draw colors to connections
                    """
                    if connection_weights:
                        color = self.change_connection_weight_value()
                        self.connection_colors[layer_index, start_index, end_index]
                    """

    def draw_layer(self, layer, num_neurons):
        created_canvas_elements = []
        center_shift = (self.canvas_height - (self.neuron_size * num_neurons + self.neuron_gap * (num_neurons-1))
                        - 2 * self.neuron_y_padding) / 2

        for i in range(num_neurons):

            x0 = self.layer_gap * (layer-1) + self.neuron_x_padding
            y0 = self.neuron_size * i + self.neuron_gap * (i-1) + self.neuron_y_padding + center_shift

            neuron_element = self.canvas.create_oval(x0, y0, x0+self.neuron_size, y0+self.neuron_size,
                                                     fill=self.neuron_normal_color)
            created_canvas_elements.append(neuron_element)
            self.canvas.tag_bind(neuron_element, "<Enter>", lambda e, n=neuron_element: self.on_neuron_enter(e, n))
            self.canvas.tag_bind(neuron_element, "<Leave>", lambda e, n=neuron_element: self.on_neuron_leave(e, n))

            # TODO Add Text to neuron
            text_pos = [x0 + self.neuron_size / 2, y0 + self.neuron_size / 2]
            # state=tk.DISABLED prevents mouse hover from blocking the neuron hover
            self.canvas.create_text(text_pos, text="WIP", font=Font(size=8), state=tk.DISABLED)

        return created_canvas_elements

    def draw_layers(self, layer):
        for i in range(len(layer)):

            x = self.neuron_x_padding + (self.layer_gap-self.neuron_size)/2 + self.layer_gap * i + self.neuron_size
            color = self.input_layer_bg if i == 0 else self.output_layer_bg if i == len(layer)-1 else self.hidden_layer_alternating_bgs[i % 2]
            layer_text = "Input Layer"if i == 0 else "Output Layer" if i == len(layer)-1 else f"Hidden Layer {i}"

            new_layer_bg = self.canvas.create_rectangle(x-self.layer_gap, 0, x, self.canvas_height, fill=color, outline="")
            self.canvas.create_text(x-self.layer_gap/2, 15, text=layer_text)
            self.canvas.create_text(x-self.layer_gap / 2, self.canvas_height-20, text=f"{layer[i]} Neuron" + ("s" if layer[i] != 1 else ""))
            self.layer_bgs.append(new_layer_bg)
            self.canvas.lower(new_layer_bg)

        print(self.layer_bgs)

    def on_neuron_enter(self, _, neuron_element):
        self.canvas.itemconfigure(neuron_element, fill=self.neuron_hover_color)

        # convert the canvas id to the information about the layer and position of the neuron
        neuron_layer, neuron_position = 0, 0  # Placeholder values
        for i, layer in enumerate(self.layer_neuron_elements):
            if neuron_element in layer:
                neuron_layer, neuron_position = i, layer.index(neuron_element)
                break

        for connection_element in self.connection_elements:
            if (connection_element[0] == neuron_layer and connection_element[1] == neuron_position) or \
                    (connection_element[0] == neuron_layer-1 and connection_element[2] == neuron_position):
                self.canvas.itemconfigure(self.connection_elements[connection_element], width=2)
            else:
                self.canvas.itemconfigure(self.connection_elements[connection_element],
                                          fill=self.connection_background_color)
                self.canvas.lower(self.connection_elements[connection_element])

        # Set all layer backgrounds back
        for layer_bg in self.layer_bgs:
            self.canvas.lower(layer_bg)

    def on_neuron_leave(self, _, neuron_element):
        self.canvas.itemconfigure(neuron_element, fill=self.neuron_normal_color)
        for connection_element in self.connection_elements:
            try:
                new_color = rgb(self.connection_colors[connection_element])
            except KeyError:
                new_color = self.connection_normal_color

            self.canvas.itemconfigure(self.connection_elements[connection_element], fill=new_color, width=1)

    def change_connection_weight_value(self, layer, start_neuron, end_neuron, weight):
        scale = 2  # TODO temp hardcoded
        connection_element = self.connection_elements[layer, start_neuron, end_neuron]
        weight = random.uniform(-1, 1)  # TODO temp hardcoded
        color = (min(max(0, int(255*(weight/scale))), 255), min(max(0, int(255*-(weight/scale))), 255), 0)
        self.canvas.itemconfigure(connection_element, fill=rgb(color))

        # save new color
        self.connection_colors[layer, start_neuron, end_neuron] = color

        return color


# translates an rgb tuple of int to a tkinter friendly color code
def rgb(rgb_vals):
    return "#%02x%02x%02x" % rgb_vals


if __name__ == "__main__":
    app = App(3, 6, 10, 8, 4, 2)
    app.mainloop()
