/* address: 0x0056961e */
/* name: CMCBuggy__ToLowerLocaleAware */
/* signature: uint __thiscall CMCBuggy__ToLowerLocaleAware(void * this, void * param_1, uint param_2) */


uint __thiscall CMCBuggy__ToLowerLocaleAware(void *this,void *param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  uint unaff_EDI;

  if (DAT_009d0998 == 0) {
    if ((0x40 < (int)param_1) && ((int)param_1 < 0x5b)) {
      param_1 = (void *)((int)param_1 + 0x20);
    }
  }
  else {
    if ((int)param_1 < 0x100) {
      if (DAT_00653a9c < 2) {
        uVar1 = (byte)PTR_DAT_00653890[(int)param_1 * 2] & 1;
      }
      else {
        uVar1 = CRT__GetCharTypeMask_Compat(this,(int)param_1,1,unaff_EDI);
      }
      if (uVar1 == 0) {
        return (uint)param_1;
      }
    }
    iVar2 = CRT__LCMapStringA_Compat();
    if (iVar2 != 0) {
      if (iVar2 == 1) {
        param_1 = (void *)((uint)this & 0xff);
      }
      else {
        param_1 = (void *)((uint)this & 0xffff);
      }
    }
  }
  return (uint)param_1;
}
