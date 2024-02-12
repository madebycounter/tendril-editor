import configparser


class Options:
    def __init__(self, **kwargs):
        self.PAN_BUTTON = kwargs.get("pan_button", 2)
        self.ZOOM_IN_BUTTON = kwargs.get("zoom_in_button", 4)
        self.ZOOM_OUT_BUTTON = kwargs.get("zoom_out_button", 5)
        self.ZOOM_SPEED = kwargs.get("zoom_speed", 0.4)
        self.MAX_ZOOM = kwargs.get("max_zoom", 8)
        self.MIN_ZOOM = kwargs.get("min_zoom", -8)
        self.IMAGE_HEIGHT = kwargs.get("image_height", 1000)
        self.HOVER_RANGE = kwargs.get("hover_range", 7)
        self.HISTORY_SIZE = kwargs.get("history_size", 100)
        self.PRIMARY_COLOR = kwargs.get("primary_color", (255, 0, 0))
        self.HOVER_COLOR = kwargs.get("hover_color", (0, 0, 255))
        self.ALTERNATE_COLOR = kwargs.get("alternate_color", (0, 255, 0))
        self.PARENT_COLOR = kwargs.get("parent_color", (0, 170, 0))
        self.ANIMATE_COLOR = kwargs.get("animate_color", (0, 200, 255))
        self.ANIMATE_SAMPLES = kwargs.get("animate_samples", 50)
        self.ANIMATE_SPEED = kwargs.get("animate_speed", 5000)
        self.BACKGROUND_COLOR = kwargs.get("background_color", (0, 0, 0))
        self.TEXT_COLOR = kwargs.get("text_color", (255, 255, 255))
        self.TEXT_BOX_COLOR = kwargs.get("text_box_color", (0, 0, 0))
        self.FONT_NAME = kwargs.get("font_name", "Comic Sans MS")
        self.FONT_SIZE = kwargs.get("font_size", 16)

    def load(self, file):
        config = configparser.ConfigParser()
        config.read(file)

        if "ImageViewer" not in config:
            config.add_section("ImageViewer")

        if "Editor" not in config:
            config.add_section("Editor")

        if "Animator" not in config:
            config.add_section("Animator")

        if "Interface" not in config:
            config.add_section("Interface")

        iv = config["ImageViewer"]
        editor = config["Editor"]
        animator = config["Animator"]
        interface = config["Interface"]

        self.PAN_BUTTON = int(iv.get("PAN_BUTTON", self.PAN_BUTTON))
        self.ZOOM_IN_BUTTON = int(iv.get("ZOOM_IN_BUTTON", self.ZOOM_IN_BUTTON))
        self.ZOOM_OUT_BUTTON = int(iv.get("ZOOM_OUT_BUTTON", self.ZOOM_OUT_BUTTON))
        self.ZOOM_SPEED = float(iv.get("ZOOM_SPEED", self.ZOOM_SPEED))
        self.MAX_ZOOM = int(iv.get("MAX_ZOOM", self.MAX_ZOOM))
        self.MIN_ZOOM = int(iv.get("MIN_ZOOM", self.MIN_ZOOM))
        self.IMAGE_HEIGHT = int(iv.get("IMAGE_HEIGHT", self.IMAGE_HEIGHT))

        self.HOVER_RANGE = int(editor.get("HOVER_RANGE", self.HOVER_RANGE))
        self.HISTORY_SIZE = int(editor.get("HISTORY_SIZE", self.HISTORY_SIZE))
        self.PRIMARY_COLOR = hex_to_rgb(
            editor.get("PRIMARY_COLOR", rgb_to_hex(self.PRIMARY_COLOR))
        )
        self.HOVER_COLOR = hex_to_rgb(
            editor.get("HOVER_COLOR", rgb_to_hex(self.HOVER_COLOR))
        )
        self.ALTERNATE_COLOR = hex_to_rgb(
            editor.get("ALTERNATE_COLOR", rgb_to_hex(self.ALTERNATE_COLOR))
        )
        self.PARENT_COLOR = hex_to_rgb(
            editor.get("PARENT_COLOR", rgb_to_hex(self.PARENT_COLOR))
        )

        self.ANIMATE_COLOR = hex_to_rgb(
            animator.get("ANIMATE_COLOR", rgb_to_hex(self.ANIMATE_COLOR))
        )
        self.ANIMATE_SAMPLES = int(
            animator.get("ANIMATE_SAMPLES", self.ANIMATE_SAMPLES)
        )
        self.ANIMATE_SPEED = int(animator.get("ANIMATE_SPEED", self.ANIMATE_SPEED))

        self.BACKGROUND_COLOR = hex_to_rgb(
            interface.get("BACKGROUND_COLOR", rgb_to_hex(self.BACKGROUND_COLOR))
        )
        self.TEXT_COLOR = hex_to_rgb(
            interface.get("TEXT_COLOR", rgb_to_hex(self.TEXT_COLOR))
        )
        self.TEXT_BOX_COLOR = hex_to_rgb(
            interface.get("TEXT_BOX_COLOR", rgb_to_hex(self.TEXT_BOX_COLOR))
        )
        self.FONT_NAME = interface.get("FONT_NAME", self.FONT_NAME)
        self.FONT_SIZE = int(interface.get("FONT_SIZE", self.FONT_SIZE))

    def save(self, file):
        config = configparser.ConfigParser()
        config.add_section("ImageViewer")
        config.set("ImageViewer", "PAN_BUTTON", str(self.PAN_BUTTON))
        config.set("ImageViewer", "ZOOM_IN_BUTTON", str(self.ZOOM_IN_BUTTON))
        config.set("ImageViewer", "ZOOM_OUT_BUTTON", str(self.ZOOM_OUT_BUTTON))
        config.set("ImageViewer", "ZOOM_SPEED", str(self.ZOOM_SPEED))
        config.set("ImageViewer", "MAX_ZOOM", str(self.MAX_ZOOM))
        config.set("ImageViewer", "MIN_ZOOM", str(self.MIN_ZOOM))
        config.set("ImageViewer", "IMAGE_HEIGHT", str(self.IMAGE_HEIGHT))

        config.add_section("Editor")
        config.set("Editor", "HOVER_RANGE", str(self.HOVER_RANGE))
        config.set("Editor", "HISTORY_SIZE", str(self.HISTORY_SIZE))
        config.set("Editor", "PRIMARY_COLOR", rgb_to_hex(self.PRIMARY_COLOR))
        config.set("Editor", "HOVER_COLOR", rgb_to_hex(self.HOVER_COLOR))
        config.set("Editor", "ALTERNATE_COLOR", rgb_to_hex(self.ALTERNATE_COLOR))
        config.set("Editor", "PARENT_COLOR", rgb_to_hex(self.PARENT_COLOR))

        config.add_section("Animator")
        config.set("Animator", "ANIMATE_COLOR", rgb_to_hex(self.ANIMATE_COLOR))
        config.set("Animator", "ANIMATE_SAMPLES", str(self.ANIMATE_SAMPLES))
        config.set("Animator", "ANIMATE_SPEED", str(self.ANIMATE_SPEED))

        config.add_section("Interface")
        config.set("Interface", "BACKGROUND_COLOR", rgb_to_hex(self.BACKGROUND_COLOR))
        config.set("Interface", "TEXT_COLOR", rgb_to_hex(self.TEXT_COLOR))
        config.set("Interface", "TEXT_BOX_COLOR", rgb_to_hex(self.TEXT_BOX_COLOR))
        config.set("Interface", "FONT_NAME", self.FONT_NAME)
        config.set("Interface", "FONT_SIZE", str(self.FONT_SIZE))

        with open(file, "w") as f:
            config.write(f)


def hex_to_rgb(hex):
    return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "{:02x}{:02x}{:02x}".format(*rgb)
