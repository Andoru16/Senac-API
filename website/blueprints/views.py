# *Imports*
from flask import Blueprint, render_template, url_for, redirect, flash, Flask, request, jsonify
from pathlib import Path
import json
import uuid
import requests
import datetime
import random
from collections import defaultdict

# *Definitions*
#   *Variables*
views = Blueprint("views", __name__)
app = Flask(__name__)
monthly_stats_file = "website/static/transactions/monthly_stats.json"

# *Routes*
@views.route("/")
@views.route("/home",methods=['GET', 'POST'])
def home():
    title = "Mercadinho Online"
    return render_template("mercadinho.html", title=title)   

@views.route("/comprar", methods=['GET', 'POST'])
def comprar():
    if request.method == 'POST':
        transaction = {
            "transaction": {
                "produto": str("Computador"),
                "preco": float(1500),
                "transaction_id": str(uuid.uuid4())
            }
        }
        try:
            response = requests.post("http://127.0.0.1:5555/api-transaction", json=transaction)
        
            if response.json()["status"] == 'success':
                flash("Compra realizada com sucesso!","success")
                return redirect(url_for("views.home"))
            elif response.json()["status"] == 'denied':
                flash("Compra negada pelo banco, por favor, entrar em contato com eles","danger")
                return redirect(url_for("views.home"))
            else:
                flash("Erro na compra!","danger")
                return redirect(url_for("views.home"))
        except Exception as e:
            flash(str(e), 'danger')  # Convert the exception to a string before flashing
            return redirect(url_for('views.home'))
        
@views.route("/api-comprar", methods=["POST"])
def api_comprar():
    try:
        compra = request.json["compra"]
        if not compra["produto"] or not compra["preco"]:
            error = {
                "status": "error",
                "message": "Produto ou Preço não especificado corretamente"
            }
            return jsonify(error)

        transaction = {
            "transaction": {
                "produto": str(compra["produto"]),
                "preco": float(compra["preco"]),
                "transaction_id": str(uuid.uuid4()),
            }
        }

        response = requests.post("http://127.0.0.1:5555/api-transaction", json=transaction)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"status": "error", "message": "Failed to make a transaction"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    

# ... (previous code)

@views.route("/api-transaction", methods=['POST'])
def api_transaction():
    global monthly_stats  # Make the dictionary global

    try:
        transaction = request.json["transaction"]
        transaction_date = datetime.datetime.now().strftime("%Y-%m")
        transaction_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        # Generate a random boolean for transaction approval
        transaction_approved = random.choice([True, False])

        if transaction_approved:
            response = {
                "status": "success",
                "message": "Compra realizada com sucesso!",
                "time": transaction_time,
                "transaction": transaction
            }
        else:
            response = {
                "status": "denied",
                "message": "Compra Negada pelo banco!",
                "time": transaction_time,
                "transaction": transaction
            }

        try:
            # Create the directory if it doesn't exist
            transaction_directory = Path("website/static/transactions/")
            transaction_directory.mkdir(parents=True, exist_ok=True)

            # Load existing monthly stats if file exists
            if Path(monthly_stats_file).exists():
                with open(monthly_stats_file, 'r') as stats_file:
                    monthly_stats = json.load(stats_file)
            else:
                monthly_stats = {}  # Initialize monthly_stats if the file doesn't exist

            # Check if the date already exists in monthly_stats
            if transaction_date not in monthly_stats:
                monthly_stats[transaction_date] = {
                    'Y_M': transaction_date,
                    'total_transactions': 0,
                    'total_price': 0.0,
                    'total_denied': 0,
                    'total_accept': 0,
                }

            monthly_stats[transaction_date]['total_transactions'] += 1
            monthly_stats[transaction_date]['total_price'] += float(transaction["preco"]) if response["status"] == "success" else 0
            monthly_stats[transaction_date]['total_denied'] += 1 if response["status"] == "denied" else 0
            monthly_stats[transaction_date]['total_accept'] += 1 if response["status"] == "success" else 0

            # Create a json file for the transaction
            transaction_file_path = transaction_directory / (transaction_date + "_transaction.json")
            transaction_file_path.write_text(json.dumps(response))

            # Create a json file for aggregated statistics
            with open(monthly_stats_file, 'w') as stats_file:
                json.dump(monthly_stats, stats_file)

            # Also create last_transaction.json
            last_transaction_file_path = transaction_directory / "last_transaction.json"
            last_transaction_file_path.write_text(json.dumps(response))
        except FileNotFoundError as e:
            print(f'File not found error: {str(e)}')
            return jsonify({"status": "error", "message": "File not found"})
        except PermissionError as e:
            print(f'Permission error: {str(e)}')
            return jsonify({"status": "error", "message": "Permission error"})
        except Exception as e:
            print(f'Unexpected error: {str(e)}')
            return jsonify({"status": "error", "message": str(e)})

        return jsonify(response)

    except KeyError as e:
        print(f'KeyError: {str(e)}')
        return jsonify({"status": "error", "message": f"KeyError: {str(e)}"})
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return jsonify({"status": "error", "message": str(e)})

# ... (remaining code)

@views.route("/monthly", methods=["GET"])
def monthly():
    if request.method == 'GET':
        monthly = request.json['Y_M']
        transaction_date = datetime.datetime.now().strftime("%Y-%m")
        try:
            transaction_directory = Path("website/static/transactions/")
            monthly_stats_file = transaction_directory / ("monthly_stats.json")
            try:
                with open(monthly_stats_file, 'r') as stats_file:
                    stats_data = json.load(stats_file)
                    if monthly in stats_data:
                        return jsonify(stats_data[monthly])
                    else:
                        return jsonify(stats_data[transaction_date])
            except Exception as e:
                print(f'Unexpected error: {str(e)}')
                return jsonify({"status": "error", "message": str(e)})
        except Exception as e:
            print(f'Unexpected error: {str(e)}')
            return jsonify({"status": "error", "message": str(e)})


@views.route("/last", methods=['GET'])
def last():
    if request.method == "GET":
        transaction_time = datetime.datetime.now().strftime("%Y-%m")
        try:
            # Read the content of last_transaction.json
            transaction_directory = Path("website/static/transactions/")
            last_transaction_file_path = transaction_directory / (transaction_time + "_stats.json")
            
            # Check if the file exists before reading
            if last_transaction_file_path.exists():
                with last_transaction_file_path.open() as file:
                    last_transaction_data = json.load(file)
                    
                # Delete the last_transaction.json file
                last_transaction_file_path.unlink()
                
                return jsonify(last_transaction_data)
            else:
                return jsonify({"status": "error", "message": "No last transaction found"})
        except Exception as e:
            print(f'Ocorreu um erro ao ler o arquivo: {str(e)}')
            return jsonify({"status": "error", "message": "Error reading last transaction"})