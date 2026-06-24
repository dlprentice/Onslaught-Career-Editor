/* address: 0x004eba30 */
/* name: CEngine__Helper_004eba30 */
/* signature: void __stdcall CEngine__Helper_004eba30(int param_1) */


void CEngine__Helper_004eba30(int param_1)

{
  int value;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  undefined4 local_4;

  if ((DAT_0089d680 == '\0') || (DAT_00889068 == -0x1234568)) {
    value = 0;
  }
  else {
    local_4 = DAT_006fbdfc;
    local_10 = 0;
    local_c = 0;
    local_8 = 0xbf800000;
    (**(code **)(*DAT_00888a50 + 0xdc))(DAT_00888a50,0,&local_10);
    value = 1;
  }
  if ((char)param_1 != '\0') {
    RenderState_SetRaw(0x98,value);
    return;
  }
  RenderState_Set(0x98,value);
  return;
}
