import argparse
import random

import computergym
import gym
from llm_agent import LLMAgent

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import logging

logging.basicConfig(level=logging.INFO)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default="click-button")
    parser.add_argument("--num-episodes", type=int, default=10)
    parser.add_argument("--llm", type=str, default="chatgpt")
    parser.add_argument("--erci", type=int, default=0)
    parser.add_argument("--step", type=int, default=-1)
    parser.add_argument("--irci", type=int, default=1)
    parser.add_argument("--sgrounding", action="store_true", default=False)
    parser.add_argument("--headless", action="store_true", default=False)
    parser.add_argument("--goal", type=str, default=None)

    opt = parser.parse_args()

    return opt


def web(opt, url):
    driver = get_webdriver(url)

    while True:
        llm_agent = LLMAgent(
            opt.env, rci_plan_loop=opt.erci, rci_limit=opt.irci, llm=opt.llm
        )

        html_body = get_html_state_from_real(driver, opt)

        llm_agent.update_html_state(html_body)

        # Set objective (e.g., login with id and pw)
        goal = opt.goal
        if goal is None:
            goal = input("Type your command (type 'exit' to quit): ")
        if goal == "exit":
            break
        llm_agent.set_goal(goal)

        llm_agent.initialize_plan()
        print(llm_agent.current_plan)

        step = llm_agent.get_plan_step()
        logging.info(f"The number of generated action steps: {step}")
        for _ in range(step):
            instruction = llm_agent.generate_action()
            print(instruction)

            perform_instruction(driver, instruction)

            html_body = get_html_state_from_real(driver, opt)
            llm_agent.update_html_state(html_body)

    driver.quit()


def get_html_state_from_real(driver, opt):
    if opt.env == "facebook":
        main_html_xpath = '//*[@id="content"]'
        html_body = driver.find_element(By.XPATH, main_html_xpath).get_attribute(
            "outerHTML"
        )
    elif opt.env == "canada":
        main_html_xpath = "//body"
        html_body = driver.find_element(By.XPATH, main_html_xpath).get_attribute(
            "outerHTML"
        )
        import re

        html_body = re.sub(r"\n", " ", html_body)
        html_body = re.sub(r"[\s]*<", r"<", html_body)
        # html_body = re.sub(r'</div>', r'</div>\n', html_body)
        html_body = re.sub(r"<div></div>", "", html_body)
        # remove useless http attributes
        html_body = re.sub(r' target="[^"]*"', "", html_body)
        html_body = re.sub(r' class="[^"]*"', "", html_body)
        html_body = re.sub(r' style="[^"]*"', "", html_body)
        html_body = re.sub(r' autocomplete="[^"]*"', "", html_body)
        html_body = re.sub(r' autofocus="[^"]*"', "", html_body)
        html_body = re.sub(r' rel="[^"]*"', "", html_body)
        html_body = re.sub(r' href="[^"]*"', "", html_body)
        html_body = re.sub(r' xmlns="[^"]*"', "", html_body)
        html_body = re.sub(r' tabindex="[^"]*"', "", html_body)
        # remove style, script, img tags
        html_body = re.sub(r"<style((?!<style).)*</style>", "", html_body)
        html_body = re.sub(r"<script((?!<script).)*</script>", "", html_body)
        html_body = re.sub(r"<img((?!</img>).)*</img>", "", html_body)
        html_body = re.sub(r"<img[^>]*>", "", html_body)
        html_body = re.sub(r"</img[^>]*>", "", html_body)
        # remove other stuff
        html_body = re.sub(r' data-[^=]*="[^"]*"', "", html_body)
        html_body = re.sub(r' aria-[^=]*="[^"]*"', "", html_body)
        html_body = re.sub(r' role="[^"]*"', "", html_body)
        html_body = re.sub(r"<!--((?!-->).)*-->", "", html_body)
        html_body = re.sub(r"<iframe((?!</iframe>).)*</iframe>", "", html_body)

    elif opt.env == "googleflight":
        main_html_xpath = '//*[@role="main"]/..'
        html_body = driver.find_element(By.XPATH, main_html_xpath).get_attribute(
            "outerHTML"
        )

        import re

        html_body = re.sub(r"\n", " ", html_body)
        # remove js attributes
        html_body = re.sub(r' jscontroller="[^"]*"', "", html_body)
        html_body = re.sub(r' jsname="[^"]*"', "", html_body)
        html_body = re.sub(r' jsaction="[^"]*"', "", html_body)
        html_body = re.sub(r' jsrenderer="[^"]*"', "", html_body)
        html_body = re.sub(r' jsshadow="[^"]*"', "", html_body)
        html_body = re.sub(r' jslog="[^"]*"', "", html_body)
        html_body = re.sub(r' jsdata="[^"]*"', "", html_body)
        html_body = re.sub(r' jsmodel="[^"]*"', "", html_body)
        html_body = re.sub(r' jsslot="[^"]*"', "", html_body)
        html_body = re.sub(r' jsowner="[^"]*"', "", html_body)
        # remove useless http attributes
        html_body = re.sub(r' target="[^"]*"', "", html_body)
        html_body = re.sub(r' class="[^"]*"', "", html_body)
        html_body = re.sub(r' style="[^"]*"', "", html_body)
        html_body = re.sub(r' autocomplete="[^"]*"', "", html_body)
        html_body = re.sub(r' autofocus="[^"]*"', "", html_body)
        html_body = re.sub(r' rel="[^"]*"', "", html_body)
        html_body = re.sub(r' href="[^"]*"', "", html_body)
        html_body = re.sub(r' xmlns="[^"]*"', "", html_body)
        html_body = re.sub(r' tabindex="[^"]*"', "", html_body)
        # remove accessibility attributes
        html_body = re.sub(r' aria-[^=]*="[^"]*"', "", html_body)
        # remove data attributes
        # html_body = re.sub(r' data-ved="[^"]*"', '', html_body)
        # html_body = re.sub(r' data-hveid="[^"]*"', '', html_body)
        html_body = re.sub(r' data-[^=]*="[^"]*"', "", html_body)
        # remove svgs
        html_body = re.sub(r"<svg((?!<svg).)*</svg>", "", html_body)
        # remove (non-nested) anonymous html containers
        while True:
            html_body, replacements = re.subn(
                r"<div>(((?!<div).)*)</div>", r"\g<1>", html_body
            )
            if replacements == 0:
                break
        while True:
            html_body, replacements = re.subn(
                r"<span>(((?!<span).)*)</span>", r"\g<1>", html_body
            )
            if replacements == 0:
                break
    else:
        raise NotImplemented

    with open("html_body.xml", "w") as f:
        f.write(html_body)

    return html_body


def perform_instruction(driver, instruction):
    instruction = instruction.split(" ")
    inst_type = instruction[0]
    inst_type = inst_type.lower()

    if inst_type == "type":
        characters = " ".join(instruction[1:])
        characters = characters.replace('"', "")
        chain = ActionChains(driver)
        chain.send_keys(characters)
        chain.perform()
    elif inst_type == "clickxpath":
        xpath = " ".join(instruction[1:])
        element = driver.find_element(By.XPATH, str(xpath))
        chain = ActionChains(driver)
        chain.move_to_element(element).click().perform()
    elif inst_type == "press":
        key_type = instruction[1]
        key_type = key_type.lower()
        # TODO: press special key
        keys = {
            "enter": Keys.ENTER,
            "space": Keys.SPACE,
            "backspace": Keys.BACKSPACE,
            "arrowleft": Keys.LEFT,
            "arrowright": Keys.RIGHT,
            "arrowup": Keys.UP,
            "arrowdown": Keys.DOWN,
            "tab": Keys.TAB,
        }
        if not key_type in keys:
            raise NotImplemented

        chain = ActionChains(driver)
        chain.send_keys(keys[key_type])
        chain.perform()

    else:
        raise ValueError("Invalid instruction")


def get_webdriver(url):
    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    options.add_argument("disable-gpu")
    options.add_argument("no-sandbox")
    options.add_argument("window-size=720")

    driver = webdriver.Chrome(options=options)
    # driver.implicitly_wait(5)
    # driver.maximize_window()
    # driver.implicitly_wait(5)

    driver.get(url)
    driver.implicitly_wait(10)
    return driver


def miniwob(opt):
    env = gym.make("MiniWoBEnv-v0", env_name=opt.env, headless=opt.headless)

    success = 0
    for _ in range(opt.num_episodes):
        llm_agent = LLMAgent(
            opt.env,
            rci_plan_loop=opt.erci,
            rci_limit=opt.irci,
            llm=opt.llm,
            state_grounding=opt.sgrounding,
        )
        # initialize environment
        states = env.reset(seeds=[random.random()], record_screenshots=True)
        llm_agent.set_goal(states[0].utterance)
        html_state = get_html_state(opt, states)

        llm_agent.update_html_state(html_state)

        try:
            llm_agent.initialize_plan()
        except:
            continue

        if opt.step == -1:
            step = llm_agent.get_plan_step()
        else:
            step = opt.step

        logging.info(f"The number of generated action steps: {step}")

        for _ in range(step):
            assert len(states) == 1
            try:
                instruction = llm_agent.generate_action()
                logging.info(f"The executed instruction: {instruction}")

                miniwob_action = llm_agent.convert_to_miniwob_action(instruction)

                states, rewards, dones, _ = env.step([miniwob_action])
            except ValueError:
                print("Invalid action or rci action fail")
                rewards = [0]
                dones = [True]
                break

            if rewards[0] != 0:
                break

            if all(dones):  # or llm_agent.check_finish_plan():
                break

            html_state = get_html_state(opt, states)
            llm_agent.update_html_state(html_state)

        if rewards[0] > 0:
            success += 1
            llm_agent.save_result(True)
        else:
            llm_agent.save_result(False)

        print(f"success rate: {success / opt.num_episodes}")

    env.close()


def get_html_state(opt, states):
    extra_html_task = [
        "click-dialog",
        "click-dialog-2",
        "use-autocomplete",
        "choose-date",
    ]

    html_body = states[0].html_body
    if opt.env in extra_html_task:
        html_body += states[0].html_extra
    return html_body


if __name__ == "__main__":
    opt = parse_opt()
    if opt.env == "googleflight":
        url = "https://www.google.com/travel/flights?hl=en"
        web(opt, url)
    elif opt.env == "canada":
        # url = "https://www.canada.ca/en.html"
        url = "https://www.canada.ca/en.html?wbdisable=true"
        web(opt, url)
    elif opt.env == "facebook":
        url = "https://www.facebook.com/"
        web(opt, url)
    else:
        miniwob(opt)
