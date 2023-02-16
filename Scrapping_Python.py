import requests  # requests library (usage : make the requests at an url)
from bs4 import BeautifulSoup  # beautifulsoup library (usage : parse the html code to select data and next collect them)
import csv  # csv library (usage : open and write in a csv)

'''
Main idea/logic/objectives of the program

Goal : Scrap the ads of car on the website "www.lacentrale.fr", filters can be add to the scrap
       and create an csv file (ordered) with the data scrap before

2 methods of scrap :
The "Dev" method -> fill parameters manually (in the code, in the call of the user_url function)
The "User" method -> the code automatically asks you what filters you want
'''

def user_url(energy, brand, kms_max, kms_min, page, price_max, price_min, year_max, year_min) :
    '''
    function who create the url of the web site that we gonna scrap

    parameters :
        energy -> str
        brand -> str
        kms_max -> str
        kms_min -> str
        page -> str
        price_max -> str
        price_min -> str
        year_max -> str
        year_min -> str

    return :
        tuple -> (url -> str, brand_space -> int)
    '''
    url_lacentrale = 'https://www.lacentrale.fr/listing?energies={energy_url}&makesModelsCommercialNames={brand_url}&mileageMax={kms_max_url}&mileageMin={kms_min_url}&options=&page={page_url}&priceMax={price_max_url}&priceMin={price_min_url}&yearMax={year_max_url}&yearMin={year_min_url}'
    url = url_lacentrale.format(energy_url = energy, brand_url = brand, kms_max_url = kms_max, kms_min_url = kms_min, page_url = page, price_max_url = price_max, price_min_url = price_min, year_max_url = year_max, year_min_url = year_min)

    brand_space = 0
    letter = 0
    while letter != len(brand)-1 :
        if brand[letter] == '%' :
            brand_space += 1
        letter += 1
    
    if int(page) == 1 :
        print('\n' + url)
    
    return (url, brand_space)

def scrap_listing(url, page) :
    '''
    function who make the request of the url make before to the server

    parameters :
        url -> str
        page -> int

    return :
        result.text -> str (the html of the page scrapped)
    '''
    result = requests.get(url)
    if page == 1 :
        print('\nÉtat de la requête :', result)
        result_user = str(result)
        if result_user == '<Response [200]>' :
            print('\n     Connexion à la page établie !\n     Scrapping en cours...')
    return result.text


def scrap_card(html_page, brand_space, fd, csv_writer) :
    '''
    function who recover all the informations we want and send them on a function to be include in the csv file

    parameters :
        html_page -> str
        brand_space -> int
        fd -> var (file descriptor, opener of csv file)
        csv_writer -> var (csv writer of the file descriptor)
    
    return :
        no returns, data are only transmitted to an other function for the purpose of being inserted into the csv file
    '''
    soup = BeautifulSoup(html_page, 'html.parser')

    for card in soup.find_all('div', 'Vehiculecard_Vehiculecard_cardBody') :
        car_name = card.find('h3')
        car_name_var = car_name.get_text()
        #print(car_name_var)

        car_brand_var = ''
        i = 0
        for space in range(1, brand_space+2) :
            if space != 1 :
                car_brand_var += car_name_var[i]
                i += 1
            while car_name_var[i] != ' ' :
                car_brand_var += car_name_var[i]
                i += 1
        #print(car_brand_var)
        #print(type(car_brand_var))

        car_model_var = ''
        for j in range(i+1, len(car_name_var)) :
            car_model_var += car_name_var[j]
        #print(car_model_var)
        #print(type(car_model_var))

        car_motor = card.find('div', 'Text_Text_text Vehiculecard_Vehiculecard_subTitle Text_Text_body2')
        car_motor_var = car_motor.get_text()
        #print(car_motor_var)
        #print(type(car_motor_var))

        car_price = card.find('span', 'Text_Text_text Vehiculecard_Vehiculecard_price Text_Text_subtitle2')
        car_price_var = car_price.get_text()
        #print(car_price_var)
        #print(type(car_price_var))

        car_price_new = car_price_var.replace(" ", "").replace("€", '')
        car_price_var = int(car_price_new)
        #print(car_price_var)
        #print(type(car_price_var))

        car_spec_lst = []
        for spec in card.find_all('div', 'Text_Text_text Vehiculecard_Vehiculecard_characteristicsItems Text_Text_body2') :
            car_spec_var = spec.get_text()
            car_spec_lst.append(car_spec_var)
            #print(car_spec_var)
        
        car_spec_lst[0] = int(car_spec_lst[0])
        #print(type(car_spec_lst[1]))
        
        car_spec_new_var = car_spec_lst[1].replace(" ", "").replace("km", '').replace('\xa0', '')
        car_spec_new_var = int(car_spec_new_var)
        car_spec_lst[1] = car_spec_new_var
        #print(type(car_spec_new_var))
        
        csv_scripter((car_brand_var, car_model_var, car_motor_var, car_spec_lst[0], car_spec_lst[1], car_spec_lst[2], car_spec_lst[3], car_price_var), fd, csv_writer)

def csv_scripter(scrap, fd, csv_writer) :
    '''
    function who add a card to the csv file, a line on the table

    parameters :
        scrap -> tuple
        fd -> var (file descriptor, opener of csv file)
        csv_writer -> var (csv writer of the file descriptor)

    return :
        no returns, data are inserted in the csv file, on a new line in the table
    '''
    csv_writer.writerow([scrap[0], scrap[1], scrap[2], scrap[3], scrap[4], scrap[5], scrap[6], scrap[7]])

def main() :
    '''
    function main, who is charged to launch all the functions to carry out the scrapping

    parameters :
        no parameters
    
    return :
        no returns
    '''
    fd = open('file.csv', 'w')
    csv_writer = csv.writer(fd)
    csv_writer.writerow(['Brand', 'Model', 'Motor', 'Year', 'Kms', 'Box', 'Energy', 'Price'])

    mode = int(input('Mode de scrapping :\n    1 - Mode Dev\n    2 - Mode User\n'))
    while mode < 1 or mode > 2 :
        print('Choix invalide !')
        mode = int(input('Mode de scrapping :\n    1 - Mode Dev\n    2 - Mode User\n'))
    
    url_error = False

    if mode == 1 :
        for page in range(1, 10+1) :
            if url_error == False :
                url_request = user_url('dies', 'RENAULT', '1000', '80', str(page), '16600', '10300', '2020', '2000')
                html_page = scrap_listing(url_request[0], page)
                url_error = error(html_page, page)
                if url_error == False :
                    scrap_card(html_page, url_request[1], fd, csv_writer)
    else :
        user_var = user()
        for page in range(1, user_var[4]+1) :
            if url_error == False :
                url_request = user_url(user_var[0], user_var[1], user_var[2], user_var[3], str(page), user_var[5], user_var[6], user_var[7], user_var[8])
                html_page = scrap_listing(url_request[0], page)
                url_error = error(html_page, page)
                if url_error == False :
                    scrap_card(html_page, url_request[1], fd, csv_writer)
    fd.close()
    print('        Scrapping terminé !\n        Fichier CSV rempli et téléchargé sur votre ordinateur\n')

def error(html_page, page) :
    '''
    function who have for job to verify if the link is wrong or if there is no cards of car with
    the selected filtes or if there is ads of car (cards) he limits the scrap to the pages who
    contain cards to scrap

    parameters :
        html_page -> str
        page -> int
    
    returns :
        booleen -> bool
    '''
    soup = BeautifulSoup(html_page, 'html.parser')
    nb_car_card = soup.find('span', 'Text_Text_text Text_Text_headline2')
    nb_car_card_var = nb_car_card.get_text()
    nb_car_card_var = int(nb_car_card_var)
    if nb_car_card_var == 0 :
        print("Il n'y a aucune annonce avec les filtres séléctionnés !")
        return True
    elif nb_car_card_var < 17 :
        return False
    elif nb_car_card_var >= 17 * page :
        return False

def user() :
    '''
    function who have to collect all the user informations about the filter of the scrap

    parameters :
        no parameters
    
    return :
        tuple (who contain all the informations enter by the user)
    '''
    brand = int(input('Choisissez la marque de la voiture :\n   1 - Renault        2 - Peugeot\n   3 - Audi           4 - Bmw\n   5 - Mercedes       6 - Volkswagen\n   7 - Ferrari        8 - Bugatti\n   9 - Aston martin   10 - Ariel\n   11 - Alfa romeo    12 - Alpine\n   13 - Lamborghini   14 - Opel\n'))
    while brand < 1 or brand > 14 :
        print('Choix invalide !')
        brand = int(input('Choisissez la marque de la voiture :\n   1 - Renault        2 - Peugeot\n   3 - Audi           4 - Bmw\n   5 - Mercedes       6 - Volkswagen\n   7 - Ferrari        8 - Bugatti\n   9 - Aston martin   10 - Ariel\n   11 - Alfa romeo    12 - Alpine\n   13 - Lamborghini   14 - Opel\n'))
    brand_lst = ['RENAULT', 'PEUGEOT', 'AUDI', 'BMW', 'MERCEDES', 'VOLKSWAGEN', 'FERRARI', 'BUGATTI', 'ASTON%20MARTIN', 'ARIEL', 'ALFA%20ROMEO', 'ALPINE', 'LAMBORGHINI', 'OPEL']
    brand_user = brand_lst[brand-1]
    
    year_max = -2
    year_min = -1
    while year_min > year_max :
        if year_min != -1 and year_max != -2 :
            print('Choix invalide !')
            print("L'année minimum doit être strictement inférieur à l'année maximum !")
        year_max = int(input("Choisissez l'année maximum de la voiture :\n"))
        while year_max < 1900 or year_max > 2023 :
            print('Choix invalide !')
            year_max = int(input("Choisissez l'année maximum de la voiture :\n"))
        year_min = int(input("Choisissez l'année minimum de la voiture :\n"))
        while year_min < 1900 or year_min > 2023 :
            print('Choix invalide !')
            year_min = int(input("Choisissez l'année minimum de la voiture :\n"))
    year_max_user = str(year_max)
    year_min_user = str(year_min)

    kms_max = -2
    kms_min = -1
    while kms_min > kms_max :
        if kms_min != -1 and kms_max != -2 :
            print('Choix invalide !')
            print('Le nombre de kilomètres minimum doit être strictement inférieur au nombre de kilomètres maximum !')
        kms_max = int(input('Choisissez les kilomètres maximum de la voiture :\n'))
        while kms_max < 0 :
            print('Choix invalide !')
            kms_max = int(input('Choisissez les kilomètres maximum de la voiture :\n'))
        
        kms_min = int(input('Choisissez les kilomètres minimum de la voiture :\n'))
        while kms_min < 0 :
            print('Choix invalide !')
            kms_min = int(input('Choisissez les kilomètres minimum de la voiture :\n'))
    kms_max_user = str(kms_max)
    kms_min_user = str(kms_min)
    
    energy = int(input("Choisissez l'énergie de la voiture :\n  1 - Diesel        2 - Essence\n  3 - Électrique    4 - Hybrides\n"))
    while energy < 1 or energy > 4 :
        print('Choix invalide !')
        energy = int(input("Choisissez l'énergie de la voiture :\n  1 - Diesel        2 - Essence\n  3 - Électrique    4 - Hybrides\n"))
    energy_lst = ['dies', 'ess', 'elec', 'hyb']
    energy_user = energy_lst[energy-1]

    price_max = -2
    price_min = -1
    while price_min > price_max :
        if price_min != -1 and price_max != -2 :
            print('Choix invalide !')
            print('Le nombre de kilomètres minimum doit être strictement inférieur au nombre de kilomètres maximum !')
        price_max = int(input('Choisissez le prix maximum de la voiture :\n'))
        while price_max < 0 :
            print('Choix invalide !')
            price_max = int(input('Choisissez le prix maximum de la voiture :\n'))
        
        price_min = int(input('Choisissez le prix minimum de la voiture :\n'))
        while price_min < 0 :
            print('Choix invalide !')
            price_min = int(input('Choisissez le prix minimum de la voiture :\n'))
    price_max_user = str(price_max)
    price_min_user = str(price_min)

    page = int(input('Choisissez le nombre de pages que vous voulez scrapper :\n'))
    while page < 1 :
        print('Choix invalide !')
        page = int(input('Choisissez le nombre de pages que vous voulez scrapper :\n'))
    
    return (energy_user, brand_user, kms_max_user, kms_min_user, page, price_max_user, price_min_user, year_max_user, year_min_user)


main()
