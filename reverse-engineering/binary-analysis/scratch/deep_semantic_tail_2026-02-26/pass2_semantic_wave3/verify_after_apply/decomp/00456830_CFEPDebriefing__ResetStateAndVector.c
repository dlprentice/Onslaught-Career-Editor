/* address: 0x00456830 */
/* name: CFEPDebriefing__ResetStateAndVector */
/* signature: int __fastcall CFEPDebriefing__ResetStateAndVector(int param_1) */


int __fastcall CFEPDebriefing__ResetStateAndVector(int param_1)

{
  *(undefined4 *)(param_1 + 4) = 0;
  CWorldPhysicsManager__Helper_004cb040((void *)param_1);
  return param_1;
}
