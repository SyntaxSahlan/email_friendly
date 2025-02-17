import os
from colorama import init, Fore, Style
from enum import Enum
from typing import Dict, Tuple
from datetime import datetime

# Force color support
os.environ['FORCE_COLOR'] = '1'
init(autoreset=True)

class ContainerType(Enum):
    FULL = "FULL"
    REEFER = "REEFER"
    IMCO = "IMCO"
    EMPTY = "EMPTY"

class ContainerSize(Enum):
    TWENTY = "20"
    FORTY = "40"

# Free days for each container type
FREE_DAYS = {
    ContainerType.FULL: 10,
    ContainerType.REEFER: 0,
    ContainerType.IMCO: 4,
    ContainerType.EMPTY: 10
}

# Rate structures for different container types and sizes
RATES = {
    ContainerType.FULL: {
        ContainerSize.TWENTY: [(10, 20, 3), (20, 30, 5), (30, float('inf'), 7)],
        ContainerSize.FORTY: [(10, 20, 5), (20, 30, 8), (30, float('inf'), 11)]
    },
    ContainerType.REEFER: {
        ContainerSize.TWENTY: [(0, 10, 6), (10, 20, 8), (20, float('inf'), 10)],
        ContainerSize.FORTY: [(0, 10, 9), (10, 20, 12), (20, float('inf'), 15)]
    },
    ContainerType.IMCO: {
        ContainerSize.TWENTY: [(4, 20, 3), (20, 30, 5), (30, float('inf'), 7)],
        ContainerSize.FORTY: [(4, 20, 5), (20, 30, 8), (30, float('inf'), 11)]
    },
    ContainerType.EMPTY: {
        ContainerSize.TWENTY: [(10, float('inf'), 1.5)],
        ContainerSize.FORTY: [(10, float('inf'), 2.5)]
    }
}

def calculate_period_charge(start_day: int, end_day: int, rate: float) -> float:
    """Calculate charges for a specific period."""
    days_in_period = end_day - start_day
    return days_in_period * rate

def calculate_demurrage(container_type: ContainerType, 
                    container_size: ContainerSize, 
                    days: int) -> Tuple[float, Dict]:
    """
    Calculate demurrage charges for a container.
    Returns total charge and breakdown of charges by period.
    """
    if days <= FREE_DAYS[container_type]:
        return 0.0, {}

    total_charge = 0.0
    breakdown = {}
    
    for period_start, period_end, rate in RATES[container_type][container_size]:
        if days <= period_start:
            break
        
        effective_end = min(period_end, days)
        if effective_end > period_start:
            charge = calculate_period_charge(
                max(period_start, FREE_DAYS[container_type]),
                effective_end,
                rate
            )
            if charge > 0:
                period_name = f"Days {period_start+1}-{period_end if period_end != float('inf') else '∞'}"
                breakdown[period_name] = {
                    'rate': rate,
                    'days': effective_end - max(period_start, FREE_DAYS[container_type]),
                    'charge': charge
                }
                total_charge += charge

    return total_charge, breakdown

def validate_date(date_str: str) -> datetime:
    """Validate date string in DD/MM/YYYY format."""
    try:
        return datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        raise ValueError("Invalid date format. Please use DD/MM/YYYY")

def calculate_days_between(start_date: datetime, end_date: datetime) -> int:
    """Calculate the number of days between two dates (inclusive)."""
    delta = end_date - start_date
    return delta.days + 1

def main():
    print(f"{Fore.CYAN}{Style.BRIGHT}KPA Container Demurrage Calculator{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    
    # Print available container types
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Available container types:{Style.RESET_ALL}")
    for container_type in ContainerType:
        print(f"{Fore.GREEN}- {container_type.value}{Fore.RESET}")

    # Get container type
    while True:
        try:
            container_type_input = input(f"\n{Fore.MAGENTA}{Style.BRIGHT}Enter container type: {Style.RESET_ALL}").upper()
            container_type = ContainerType(container_type_input)
            break
        except ValueError:
            print(f"{Fore.RED}{Style.BRIGHT}Invalid container type. Please try again.{Style.RESET_ALL}")

    # Get container size
    while True:
        try:
            container_size_input = input(f"{Fore.MAGENTA}{Style.BRIGHT}Enter container size (20/40): {Style.RESET_ALL}")
            container_size = ContainerSize(container_size_input)
            break
        except ValueError:
            print(f"{Fore.RED}{Style.BRIGHT}Invalid container size. Please enter 20 or 40.{Style.RESET_ALL}")

    # Choose input method
    while True:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}Choose input method:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. Enter number of days")
        print(f"2. Enter date range{Style.RESET_ALL}")
        try:
            choice = int(input(f"{Fore.MAGENTA}{Style.BRIGHT}Enter your choice (1/2): {Style.RESET_ALL}"))
            if choice not in [1, 2]:
                raise ValueError
            break
        except ValueError:
            print(f"{Fore.RED}{Style.BRIGHT}Please enter a valid choice (1 or 2).{Style.RESET_ALL}")

    # Get days based on chosen method
    if choice == 1:
        while True:
            try:
                days = int(input(f"{Fore.MAGENTA}{Style.BRIGHT}Enter number of days: {Style.RESET_ALL}"))
                if days < 0:
                    raise ValueError
                break
            except ValueError:
                print(f"{Fore.RED}{Style.BRIGHT}Please enter a valid number of days.{Style.RESET_ALL}")
    else:
        while True:
            try:
                start_date_str = input(f"{Fore.MAGENTA}{Style.BRIGHT}Enter start date (DD/MM/YYYY): {Style.RESET_ALL}")
                end_date_str = input(f"{Fore.MAGENTA}{Style.BRIGHT}Enter end date (DD/MM/YYYY): {Style.RESET_ALL}")
                
                start_date = validate_date(start_date_str)
                end_date = validate_date(end_date_str)
                
                if end_date < start_date:
                    print(f"{Fore.RED}{Style.BRIGHT}End date cannot be earlier than start date.{Style.RESET_ALL}")
                    continue
                    
                days = calculate_days_between(start_date, end_date)
                break
            except ValueError as e:
                print(f"{Fore.RED}{Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

    # Calculate charges
    total_charge, breakdown = calculate_demurrage(container_type, container_size, days)

    # Display results
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Demurrage Calculation Results{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"Container Type: {Fore.GREEN}{container_type.value}{Fore.RESET}")
    print(f"Container Size: {Fore.GREEN}{container_size.value}ft{Fore.RESET}")
    print(f"Total Days: {Fore.YELLOW}{days}{Fore.RESET}")
    print(f"Free Days: {Fore.YELLOW}{FREE_DAYS[container_type]}{Fore.RESET}")
    print(f"{Fore.CYAN}{'-' * 40}{Fore.RESET}")

    if not breakdown:
        print(f"{Fore.GREEN}{Style.BRIGHT}No charges (within free period of {FREE_DAYS[container_type]} days){Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}{Style.BRIGHT}Charges Breakdown:{Style.RESET_ALL}")
        for period, details in breakdown.items():
            print(f"\n{Fore.CYAN}{period}:{Fore.RESET}")
            print(f"  Rate per day: {Fore.YELLOW}{details['rate']}{Fore.RESET} KWD")
            print(f"  Days charged: {Fore.YELLOW}{details['days']}{Fore.RESET}")
            print(f"  Charge: {Fore.YELLOW}{details['charge']}{Fore.RESET} KWD")

    print(f"\n{Fore.CYAN}{Style.BRIGHT}Total Charge: {Fore.YELLOW}{total_charge:.3f} KWD{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

