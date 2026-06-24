/* address: 0x004d28a0 */
/* name: CPlayer__Init */
/* signature: void __fastcall CPlayer__Init(int param_1) */


void __fastcall CPlayer__Init(int param_1)

{
  float fVar1;

  CPlayer__GotoFPView();
  fVar1 = PLATFORM__GetSysTimeFloat();
  *(float *)(param_1 + 0x4c) = fVar1;
  return;
}
