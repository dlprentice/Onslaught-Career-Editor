/* address: 0x00472650 */
/* name: CGame__IsRunningResources */
/* signature: bool __fastcall CGame__IsRunningResources(int param_1) */


bool __fastcall CGame__IsRunningResources(int param_1)

{
  return DAT_006317cc == *(int *)(param_1 + 0x30);
}
