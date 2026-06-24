/* address: 0x004d28a0 */
/* name: CPlayer__Unk_004d28a0 */
/* signature: void __fastcall CPlayer__Unk_004d28a0(int param_1) */


void __fastcall CPlayer__Unk_004d28a0(int param_1)

{
  float fVar1;

  CPlayer__dtor();
  fVar1 = PLATFORM__GetSysTimeFloat();
  *(float *)(param_1 + 0x4c) = fVar1;
  return;
}
