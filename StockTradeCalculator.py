#Soufiane El Mameri 3096602
import sys
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLabel, QComboBox, QCalendarWidget, QDialog, QApplication, QGridLayout, QSpinBox, \
    QDoubleSpinBox
from datetime import datetime
import csv


class StockTradeProfitCalculator(QDialog):
    '''
    Provides the following functionality:

    - Allows the selection of the stock to be purchased
    - Allows the selection of the quantity to be purchased
    - Allows the selection of the purchase date
    - Displays the purchase total
    - Allows the selection of the sell date
    - Displays the sell total
    - Displays the profit total
    '''

    def __init__(self):
        '''
        This method requires substantial updates.
        Each of the widgets should be suitably initialized and laid out.
        '''
        super().__init__()

        # setting up dictionary of Stocks
        self.data = self.make_data()

        # Check if 'Amazon' exists, if not, handle it gracefully
        if 'Amazon' in self.data:
            self.sellCalendarDefaultDate = sorted(self.data['Amazon'].keys())[-1]
            most_recent_sell_date = QDate(self.sellCalendarDefaultDate[0], self.sellCalendarDefaultDate[1],
                                          self.sellCalendarDefaultDate[2])
            # define buyCalendarDefaultDate two weeks earlier
            self.buyCalendarDefaultDate = most_recent_sell_date.addDays(-14)
        else:
            print("Amazon not found in the dataset. Available stocks:", self.data.keys())
            self.sellCalendarDefaultDate = QDate.currentDate()  # Default to the current date
            self.buyCalendarDefaultDate = QDate.currentDate().addDays(-14)  #Default to two weeks before current date

        # QLabel for Stock selection
        self.stockLabel = QLabel('Select Stock')
        # Creating a QComboBox and populating it with a list of Stocks
        self.stockComboBox = QComboBox(self)
        self.stockComboBox.addItems(self.data.keys())

        # creating CalendarWidgets for selection of purchase and sell dates
        self.purchaseDateLabel = QLabel('Purchase Date')
        self.purchaseCalendar = QCalendarWidget(self)

        self.sellDateLabel = QLabel('Sell Date')
        self.sellCalendar = QCalendarWidget(self)

        # Quantity label
        self.quantityLabel = QLabel('Quantity')

        # Creating QSpinBox to select Stock quantity purchased
        self.quantitySpinBox = QDoubleSpinBox(self)
        self.quantitySpinBox.setRange(0.00, 1000)

        # creating QLabels to show the Stock purchase total
        self.purchaseTotalLabel = QLabel('Purchase Total: 0.00')

        # Creating Qlabels to show any date error
        self.dateError = QLabel()
        # Creating QLabels to show the Stock sell total
        self.sellTotalLabel = QLabel('Sell Total: 0.00')

        # Creating QLabels to show the Stock profit total
        self.profitLabel = QLabel('PNL: 0.00')

        # initializing the layout - 6 rows to start
        layout = QGridLayout()
        layout.setVerticalSpacing(15)

        #row 1: Stock selection
        layout.addWidget(self.stockLabel, 0 , 0)
        layout.addWidget(self.stockComboBox, 0, 1 )

        #row 2: Quantity selection
        layout.addWidget(self.quantityLabel, 1, 0)
        layout.addWidget(self.quantitySpinBox, 1, 1)

        #row 3 : Purchase date selection
        layout.addWidget(self.purchaseDateLabel, 2, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.purchaseCalendar, 3, 0 )

        #row 4: Sell date selection
        layout.addWidget(self.sellDateLabel, 2, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sellCalendar, 3, 1)

        #row 5: error message
        layout.addWidget(self.dateError, 4, 0,1,3,Qt.AlignmentFlag.AlignCenter)

        # row 6: Purchase
        layout.addWidget(self.purchaseTotalLabel, 5, 0)
        self.purchaseTotalLabel.setFixedWidth(250)

        # row 7: sell total and Profit total
        layout.addWidget(self.sellTotalLabel, 6, 0)
        self.sellTotalLabel.setFixedWidth(250)
        layout.addWidget(self.profitLabel, 6, 1, 1, 3, Qt.AlignmentFlag.AlignRight)
        self.profitLabel.setFixedWidth(200)

        self.setLayout(layout)
        #setting the calendar values
        # purchase: two weeks before most recent
        # sell: most recent
        self.purchaseCalendar.setSelectedDate(self.buyCalendarDefaultDate)
        self.sellCalendar.setSelectedDate(QDate(self.sellCalendarDefaultDate[0], self.sellCalendarDefaultDate[1], self.sellCalendarDefaultDate[2]))

        #connecting signals to slots so that a change in one control updates the UI
        self.stockComboBox.currentIndexChanged.connect(self.updateUi)
        self.purchaseCalendar.selectionChanged.connect(self.updateUi)
        self.sellCalendar.selectionChanged.connect(self.updateUi)
        self.quantitySpinBox.valueChanged.connect(self.updateUi)
        #window title
        self.setWindowTitle('Stock Trade Profit Calculator')
        self.setWindowIcon(QIcon('icon.png'))
        # TODO: update the UI

    def updateUi(self):
        '''
        This requires substantial development.
        Updates the UI when control values are changed; should also be called when the app initializes.
        '''
        try:

            # get the selected stock from the ComboBox
            stock_name = self.stockComboBox.currentText()

            # get the selected purchase and sell dates from calendars
            purchase_date = self.purchaseCalendar.selectedDate().toPyDate()
            sell_date = self.sellCalendar.selectedDate().toPyDate()

            # get the quantity from the SpinBox
            quantity = self.quantitySpinBox.value()

            # convert the selected dates to tuples (year, month, day)
            purchase_tuple = (purchase_date.year, purchase_date.month, purchase_date.day)
            sell_tuple = (sell_date.year, sell_date.month, sell_date.day)

            # get stock prices for the selected dates
            purchase_price = self.data[stock_name].get(purchase_tuple, 0)
            sell_price = self.data[stock_name].get(sell_tuple, 0)

            # check if the selected dates have data and if quantity is entered
            # if not show error message
            self.dateError.setStyleSheet("color: red;")
            if quantity == 0 :
                self.dateError.setText("Please enter the quantity")
            # check if the sell date is before purchase date
            elif sell_date < purchase_date:
                # show error
                self.dateError.setText("Sell date cannot be before purchase date")
            elif purchase_price == 0 and sell_price == 0:
                self.dateError.setText("No data found for the selected dates")
            elif purchase_price == 0:
                self.dateError.setText("No data found for the purchase date")
            elif sell_price == 0:
                self.dateError.setText("No data found for the sell date")

            else:
                # calculate the total purchase, total sell, and profit
                purchase_total = purchase_price * quantity
                sell_total = sell_price * quantity
                profit = sell_total - purchase_total

                # update the purchase sell and profit labels with the calculated totals
                self.purchaseTotalLabel.setText(f"Purchase Total: {purchase_total:.2f}")
                self.sellTotalLabel.setText(f"Sell Total: {sell_total:.2f}")

                #change profit label if its a win or loss
                if profit > 0:
                    self.profitLabel.setStyleSheet("color: green;")
                if profit < 0:
                    self.profitLabel.setStyleSheet("color: red;")

                # Update the profitLabel text
                self.profitLabel.setText(f"PNL: {profit:.2f}")
                # hide error message
                self.dateError.setText("")
            if purchase_price == 0 or sell_price == 0 or sell_date < purchase_date:
                # reset the purchase sell and profit labels to 0
                self.purchaseTotalLabel.setText("Purchase Total: 0.00")
                self.sellTotalLabel.setText("Sell Total: 0.00")
                self.profitLabel.setText("PNL: 0.00")
                # reset profit label to black color
                self.profitLabel.setStyleSheet("color: black;")

        except Exception as e:
            print(f"Error in updateUi: {e}")

    def make_data(self):
        '''
        This code reads the stock market CSV file and generates a dictionary structure.
        :return: a dictionary of dictionaries
        '''
        data = {}
        try:
            with open('Transformed_Stock_Market_Dataset.csv', mode='r') as file:
                reader = csv.DictReader(file)
                stock_names = reader.fieldnames[1:]  # All columns except 'Date' are stock names

                for row in reader:
                    date_string = row['Date']
                    date_tuple = self.string_date_into_tuple(date_string)

                    for stock in stock_names:
                        price = row[stock].replace(',', '')
                        try:
                            price = float(price)
                        except ValueError:
                            price = 0.0

                        if stock not in data:
                            data[stock] = {}

                        data[stock][date_tuple] = price

            print("Data loaded successfully.")
            print(f"Stocks available: {stock_names}")  # Debugging: Print all available stock names

        except Exception as e:
            print(f"Error reading data: {e}")
        return data

    def string_date_into_tuple(self, date_string):
        '''
        Converts a date in string format (e.g., "2024-02-02") into a tuple (year, month, day).
        :return: tuple representing the date
        '''
        try:
            if '-' in date_string:
                date_obj = datetime.strptime(date_string, "%d-%m-%Y")
            else:
                date_obj = datetime.strptime(date_string, "%m/%d/%Y")
            return date_obj.year, date_obj.month, date_obj.day
        except ValueError:
            print(f"Error parsing date: {date_string}")
            return None


# This is complete
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Adding global style to all labels
    app.setStyleSheet("""
        QDialog {
            background-color: #dddddd;  /* Light gray background */
        }
        QLabel {
            color: #333333;  /* Dark gray text */
            font-size: 16px;
            font-family: Arial;
            font-weight : bold;
        }
        QComboBox{
            background-color: #efefef;  /* White background */
            color: #333333;  /* Dark gray text */
            padding: 3px;
            font-weight : bold;
        }
        QDoubleSpinBox{
            background-color: #efefef;  /* White background */
            height: 30px;
            color: #333333;  /* Dark gray text */
            font-weight : bold;
        }
        QComboBox{
            border-bottom: 2px solid #444444;  /* Light gray border */
            border-radius: 5px;  /* Rounded corners for a smoother look */
        }
        QComboBox:hover{
            cursor: pointer;
            border-bottom: 0px solid #444444;  /* Light gray border */
            border-radius: 5px;  /* Rounded corners for a smoother look */
        }
        QComboBox::drop-down{
            width:0;
        }

    """)
    stock_calculator = StockTradeProfitCalculator()
    stock_calculator.show()
    sys.exit(app.exec())
