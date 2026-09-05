import asyncio
from dotenv import load_dotenv
from agents import InputGuardrailTripwireTriggered, Runner, SQLiteSession

from open_sdk_1.app_agents import triage_agent

load_dotenv()

# --- Interactive Terminal Loop with Session Memory ---
async def start_terminal():
    print("==================================================")
    print("🌾 WELCOME TO KISAN DOST (FARMER'S FRIEND) AGENT 🌾")
    print("   Powered by OpenAI Agents SDK & Gemini 3.6-Flash")
    print("==================================================")
    print("Type your question below (in Urdu or English). Type 'exit' or 'quit' to end.\n")

    # Persistent session memory to remember farmer details across turns
    session = SQLiteSession("kisan_dost", db_path="kisan_dost_session.db")

    while True:
        try:
            user_input = input("\n👨‍🌾 Farmer: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n🌾 Thank you for using Kisan Dost. Khuda Hafiz!")
                break

            print("\n🤖 Kisan Dost is thinking...")
            
            # Execute agent run with session context
            result = await Runner.run(
                triage_agent,
                input=user_input,
                session=session
            )

            print(f"\n🚜 Kisan Dost Response:\n{result.final_output}")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n\n🌾 Program interrupted. Goodbye!")
            break
        except InputGuardrailTripwireTriggered as e:
            message = e.guardrail_result.output.output_info
            print(f"\n🚜 Kisan Dost Response:\n{message}")
            print("-" * 50)
        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(start_terminal())