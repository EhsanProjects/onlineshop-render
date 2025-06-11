import os
# ER Diagram : https://www.convertcsv.com/sqlite-online.htm
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1"


def generate_secret_key(length=32):
    return os.urandom(length).hex()


# SECRET_KEY = generate_secret_key()
SECRET_KEY = "sdaksd$$%%asd@@jsdljka435345hsdohssasjld"

# Added
RECAPTCHA_PUBLIC_KEY = '6LdUuQcqAAAAAH4IoOikoKuVH7NJhSBbaCH_86MD'
RECAPTCHA_PRIVATE_KEY ='6LdUuQcqAAAAACN8W0_IUxBJPMLC6sgzwpaq4H8l'


PAYMENT_MERCHANT = "sandbox"
PAYMENT_CALLBACK = "http://localhost:5000/verify"
PAYMENT_FIRST_REQUEST_URL = 'https://sandbox.shepa.com/api/v1/token'
PAYMENT_VERIFY_REQUEST_URL = 'https://sandbox.shepa.com/api/v1/verify'

SITE_NAME = "Ehsan Online Shopping"
ABOUT_PAGE_HTML = """
 <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Egestas purus viverra accumsan in nisl nisi. Arcu cursus vitae congue mauris rhoncus aenean vel elit scelerisque. In egestas erat imperdiet sed euismod nisi porta lorem mollis. Morbi tristique senectus et netus. Mattis pellentesque id nibh tortor id aliquet lectus proin. Sapien faucibus et molestie ac feugiat sed lectus vestibulum. Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget. Dictum varius duis at consectetur lorem. Nisi vitae suscipit tellus mauris a diam maecenas sed enim. Velit ut tortor pretium viverra suspendisse potenti nullam. Et molestie ac feugiat sed lectus. Non nisi est sit amet facilisis magna. Dignissim diam quis enim lobortis scelerisque fermentum. Odio ut enim blandit volutpat maecenas volutpat. Ornare lectus sit amet est placerat in egestas erat. Nisi vitae suscipit tellus mauris a diam maecenas sed. Placerat duis ultricies lacus sed turpis tincidunt id aliquet. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Egestas purus viverra accumsan in nisl nisi. Arcu cursus vitae congue mauris rhoncus aenean vel elit scelerisque. In egestas erat imperdiet sed euismod nisi porta lorem mollis. Morbi tristique senectus et netus. Mattis pellentesque id nibh tortor id aliquet lectus proin. Sapien faucibus et molestie ac feugiat sed lectus vestibulum. Ullamcorper velit sed ullamcorper morbi tincidunt ornare massa eget. Dictum varius duis at consectetur lorem. Nisi vitae suscipit tellus mauris a diam maecenas sed enim. Velit ut tortor pretium viverra suspendisse potenti nullam. Et molestie ac feugiat sed lectus. Non nisi est sit amet facilisis magna. Dignissim diam quis enim lobortis scelerisque fermentum. Odio ut enim blandit volutpat maecenas volutpat. Ornare lectus sit amet est placerat in egestas erat. Nisi vitae suscipit tellus mauris a diam maecenas sed. Placerat duis ultricies lacus sed turpis tincidunt id aliquet.</p>
    <ul>
        <li><a href="tel:1111111111">+11111111111</a></li>
        <li></li>
        <li>Address: 355 Example Dr, IL, US </li>
    </ul>
"""
feature1 = "Free Shippingg"
feature2 = "%100 Original"
feature3 = "Pay at address"
feature4 = "Safe Payment"
feature5 = "30 Days Money Back Quaranteed"
# Change photoes in the static/image as you need

# Added


categories= {
        1: 'Other',
        2: 'Fragrance',
        3: 'Car',
        4: 'Mobile',
        5: 'Toys',
        6: 'Electronics'
    }


