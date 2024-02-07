import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from datetime import datetime, timedelta
import random
import re


def readlines(filename):
    with open(filename) as file:
        return file.readlines()


def writelines(filename, content):
    with open(filename, 'w') as file:
        file.writelines(content)


def generate_recipe_dictionary(recipes):
    recipe_dict = {}
    current_title = []

    for recipe in recipes:
        recipe = recipe.strip()
        if recipe.startswith('RECIPE:'):
            current_title = recipe.split(':', 1)[1].strip()
            recipe_dict[current_title] = []
        elif recipe:
            recipe_dict[current_title].append(recipe)

    return recipe_dict


def get_tags(recipe_text):
    match = re.search(r'\*\*TAGS:(.*?)\*\*', recipe_text, re.DOTALL)
    if match:
        tags_str = match.group(1).strip()
        tags = [tag.strip() for tag in tags_str.split(',')]
        return tags
    else:
        return []


def combine_duplicates(meal_plan):
    combined_dict = {}

    for item in meal_plan:
        for sub_item in item:
            if any(unit in sub_item for unit in
                   ['tsp', 'tbsp', 'cup', 'whole', 'cloves', 'oz', 'lbs', 'can', 'bag', '6-inch', 'head']
                   ):
                name, quantity, unit = sub_item.split(' ')
                quantity = float(quantity)

                if unit == 'tsp':
                    converted_quantity = round((quantity / 48), 5)
                    unit = 'cup'
                elif unit == 'tbsp':
                    converted_quantity = round((quantity / 16), 5)
                    unit = 'cup'
                elif unit == 'oz':
                    converted_quantity = round((quantity / 16), 2)
                    unit = 'lbs'
                else:
                    converted_quantity = quantity

                if name in combined_dict:
                    combined_dict[name][0] += converted_quantity
                else:
                    combined_dict[name] = [converted_quantity, unit]
            else:
                pass

    for name, (converted_quantity, unit) in combined_dict.items():
        if converted_quantity < 0.04 and unit == 'cup':
            converted_quantity = round((converted_quantity * 48), 1)
            unit = 'tsp'
        elif converted_quantity < 0.3 and unit == 'cup':
            converted_quantity = round((converted_quantity * 16), 1)
            unit = 'tbsp'
        elif converted_quantity < 0.5 and unit == 'lbs':
            converted_quantity = round((converted_quantity * 16), 1)
            unit = 'oz'

        combined_dict[name] = [converted_quantity, unit]

    result_list = [f"{name} {converted_quantity} {unit}" for name, (converted_quantity, unit) in combined_dict.items()]

    return result_list


def method_selection():
    root = tk.Tk()
    root.title("Method Selection")
    root.update_idletasks()  # Update the window info to calculate the center position
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.geometry("+%d+%d" % (x, y))

    choice = tk.StringVar()

    def choose_existing():
        choice.set('1')
        root.destroy()

    def generate_recipes():
        choice.set('2')
        root.destroy()

    label = tk.Label(root, text="Do you have recipes already picked out or would you like those generated for you?")
    label.pack(pady=10)

    button_existing = tk.Button(root, text="I have recipes", command=choose_existing)
    button_existing.pack(pady=5)

    button_generate = tk.Button(root, text="Generate recipes", command=generate_recipes)
    button_generate.pack(pady=5)

    root.mainloop()

    return choice.get()


def create_meal_plan(recipes):
    recipe_dict = generate_recipe_dictionary(recipes)
    recipe_tags = {}

    for recipe in recipes:
        recipe = recipe.strip()
        if recipe.startswith('RECIPE:'):
            current_title = recipe.split(':', 1)[1].strip()
            tags = get_tags(recipe)
            recipe_tags[current_title] = tags

    method = method_selection()

    recipe_list = []

    if method == '1':
        root = tk.Tk()
        root.title('Add Recipes')
        root.update_idletasks()  # Update the window info to calculate the center position
        x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
        y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
        root.geometry("+%d+%d" % (x, y))

        options = (list(recipe_dict.keys()))
        options.append('exit')

        selected_option = tk.StringVar(root)
        selected_option.set(options[0])

        def add_recipe():
            recipe_title = selected_option.get()
            if recipe_title == '' or recipe_title == 'exit':
                root.destroy()
            elif recipe_title not in options:
                messagebox.showerror("Error", "That is not an option, check spelling and capitals and retry.")
            elif recipe_title in recipe_list:
                messagebox.showerror('Error', 'That recipe is already in the meal plan.')
            else:
                recipe_list.append(recipe_title)
                messagebox.showinfo("Success", f"Recipe '{recipe_title}' added to the meal plan.")

        option_menu = tk.OptionMenu(root, selected_option, *options)
        option_menu.pack(padx=10, pady=10)

        add_button = tk.Button(root, text="Add Recipe", command=add_recipe)
        add_button.pack(pady=10)

        root.mainloop()

    elif method == '2':
        start = simpledialog.askstring("Start Date", "What date are you starting from? (mm.dd.yy):")
        end = simpledialog.askstring("End Date", "What date are you going to? (mm.dd.yy):")

        start_date = datetime.strptime(start, "%m.%d.%y")
        end_date = datetime.strptime(end, "%m.%d.%y")

        current_date = start_date
        meal_plan = []
        while current_date <= end_date:
            current_recipe = random.choice(list(recipe_dict.keys()))
            if not any(tag in recipe_tags[current_recipe] for tag in recipe_tags.values()) and \
                    not current_recipe in recipe_list:
                meal_plan.append((current_recipe, current_date.strftime("%m.%d")))
                recipe_list.append(current_recipe)
                current_date += timedelta(days=3)

        easy_read = ''
        for recipe_entry in meal_plan:
            recipe_title, date = recipe_entry
            easy_read += f'{date}: {recipe_title} \n'
        messagebox.showinfo("Meal Plan", f'{easy_read}')

    ingredients_list = []

    for meal_title in recipe_list:
        new_recipe_dict = {}

        index = recipe_dict[meal_title].index('Instructions:')
        new_recipe_dict[meal_title] = recipe_dict[meal_title][:index]

        ingredients_list.append(new_recipe_dict[meal_title])

    message_ingredients = ''
    consolidated_ingredients = combine_duplicates(ingredients_list)
    for ingredient in consolidated_ingredients:
        message_ingredients += f'{ingredient} \n'
    messagebox.showinfo('Shopping List', f'{message_ingredients}')


def view_recipes(recipes):
    recipe_dict = generate_recipe_dictionary(recipes)

    alphabetized_titles = sorted(recipe_dict.keys())

    for line, title in enumerate(alphabetized_titles, start=1):
        print(f'{line}. {title}')

    choice = simpledialog.askstring("Input", "Recipe:")
    if choice == 'none':
        return
    elif choice in recipe_dict:
        print(f'\nIngredients for {choice}:')
        for ingredient in recipe_dict[choice]:
            print(f'{ingredient}')
    else:
        messagebox.showinfo("Error", "Invalid choice. Please choose again.")


def edit_recipes(recipes):
    recipe_dict = generate_recipe_dictionary(recipes)
    for title in recipe_dict:
        print(f'- {title}')

    while True:
        recipe_to_edit = simpledialog.askstring("Input", "Enter the recipe name:")
        if recipe_to_edit not in recipe_dict:
            messagebox.showinfo("Error", f'{recipe_to_edit} is not an option.\n '
                                f'Please check spelling and try again, or enter a blank line to return to the menu.')
        if recipe_to_edit == '':
            return
        else:
            break

    index = recipe_dict[recipe_to_edit].index('Instructions:')
    instructions = recipe_dict[recipe_to_edit][index:]
    recipe_dict[recipe_to_edit] = recipe_dict[recipe_to_edit][:index]

    print()
    print(f'Ingredients for {recipe_to_edit}:')
    for ingredient in recipe_dict[recipe_to_edit]:
        print(f'- {ingredient}')

    print()
    action = simpledialog.askstring("Input", "Do you want to (1) edit an existing ingredient or "
                                             "(2) add a new ingredient?\nEnter 1 or 2:")
    if action == '1':
        ingredient_to_edit = simpledialog.askstring("Input", "Which ingredient do you want to edit?")
        new_measurement = simpledialog.askstring("Input", "Enter the new measurement:")

        for i, ingredient in enumerate(recipe_dict[recipe_to_edit]):
            if ingredient.startswith(ingredient_to_edit):
                parts = ingredient.split()
                parts[1] = new_measurement
                recipe_dict[recipe_to_edit][i] = ' '.join(parts)

    elif action == '2':
        new_ingredient = simpledialog.askstring("Input", "Enter a new ingredient in the following form-\n"
                                                         "Ingredient measurement (i.e. Soy_Sauce 0.5 tbsp):")
        recipe_dict[recipe_to_edit].append(new_ingredient)

    recipe_dict[recipe_to_edit].extend(instructions)

    print()
    print(f'Updated ingredients for {recipe_to_edit}:')
    for ingredient in recipe_dict[recipe_to_edit]:
        print(f'{ingredient}')
    print()


def change_directory():
    options = ['Dinner', 'Desserts']
    directory = simpledialog.askstring("Input", "Select a directory: ")
    if directory == 'Dinner':
        return 'DinnerRecipeList.txt'
    elif directory == 'Desserts':
        return 'DessertsRecipeList.txt'


def gui_create_meal_plan(infile):
    lines = readlines(infile)
    create_meal_plan(lines)


def gui_view_recipes(infile):
    lines = readlines(infile)
    view_recipes(lines)


def gui_edit_recipes(infile):
    lines = readlines(infile)
    edit_recipes(lines)


def main(infile):
    root = tk.Tk()
    root.title("Menu")

    root.update_idletasks()  # Update the window info to calculate the center position
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    root.geometry("+%d+%d" % (x, y))

    def call_create_meal_plan():
        root.destroy()
        gui_create_meal_plan(infile)

    def call_view_recipes():
        root.destroy()
        gui_view_recipes(infile)

    def call_edit_recipes():
        root.destroy()
        gui_edit_recipes(infile)

    def call_exit_program():
        root.destroy()
        root.quit()
        return

    # Create buttons for each choice
    button1 = tk.Button(root, text="Create Meal Plan", command=call_create_meal_plan)
    button2 = tk.Button(root, text="View Recipes", command=call_view_recipes)
    button3 = tk.Button(root, text="Edit Recipes", command=call_edit_recipes)
    button5 = tk.Button(root, text="Exit Program", command=call_exit_program)

    # Pack the buttons
    button1.pack(pady=5)
    button2.pack(pady=5)
    button3.pack(pady=5)
    button5.pack(pady=5)

    root.protocol("WM_DELETE_WINDOW", call_exit_program)

    root.mainloop()


if __name__ == '__main__':
    infile = 'DinnerRecipeList.txt'
    # outfile = 'new-recipes.txt'
    main(infile)




    # def main(infile, outfile):
    #     while True:
    #         infile = infile
    #         lines = readlines(infile)
    #         # print_menu()
    #         choice = simpledialog.askstring("Input", "1. Create Meal Plan\n 2.View Recipes\n 3. Edit recipes\n"
    #                                         '4. Change Directory\n 5. Exit Program\n Enter your choice (1-5):')
    #         if choice == '1':
    #             create_meal_plan(lines)
    #         elif choice == '2':
    #             view_recipes(lines)
    #         elif choice == '3':
    #             edit_recipes(lines)
    #         elif choice == '4':
    #             infile = change_directory()
    #         elif choice == '5' or '':
    #             break
    #         else:
    #             messagebox.showinfo("Error", "Invalid choice. Please enter a whole number between 1 and 5.")
