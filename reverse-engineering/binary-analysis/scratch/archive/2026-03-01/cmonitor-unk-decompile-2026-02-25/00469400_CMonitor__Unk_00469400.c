/* address: 0x00469400 */
/* name: CMonitor__Unk_00469400 */
/* signature: uint __cdecl CMonitor__Unk_00469400(int param_1, int param_2, int param_3, int param_4) */


uint __cdecl CMonitor__Unk_00469400(int param_1,int param_2,int param_3,int param_4)

{
  uint uVar1;

  uVar1 = CUnitAI__Unk_0044dea0(0x675688);
  if (uVar1 != 0) {
    return uVar1 & 0xffffff00;
  }
  uVar1 = CVBufTexture__Unk_00523cc0((float)param_1,(float)param_2,(float)param_3,(float)param_4);
  return uVar1;
}
