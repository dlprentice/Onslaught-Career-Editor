/* address: 0x00563951 */
/* name: CTexture__Helper_00563951 */
/* signature: uint __thiscall CTexture__Helper_00563951(void * this, int param_1, int param_2, uint param_3) */


uint __thiscall CTexture__Helper_00563951(void *this,int param_1,int param_2,uint param_3)

{
  int iVar1;

  if (param_1 + 1U < 0x101) {
    param_1._2_2_ = *(ushort *)(PTR_DAT_00653890 + param_1 * 2);
  }
  else {
    iVar1 = CRT__GetStringTypeACompat();
    if (iVar1 == 0) {
      return 0;
    }
  }
  return (uint)param_1._2_2_ & param_2;
}
