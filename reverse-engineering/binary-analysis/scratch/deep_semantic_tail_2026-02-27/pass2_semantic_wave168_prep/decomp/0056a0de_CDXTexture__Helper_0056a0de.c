/* address: 0x0056a0de */
/* name: CDXTexture__Helper_0056a0de */
/* signature: uint __thiscall CDXTexture__Helper_0056a0de(void * this, void * param_1, int param_2) */


uint __thiscall CDXTexture__Helper_0056a0de(void *this,void *param_1,int param_2)

{
  uint uVar1;
  uint unaff_retaddr;

  if (1 < DAT_00653a9c) {
    uVar1 = CTexture__Helper_00563951(this,(int)param_1,8,unaff_retaddr);
    return uVar1;
  }
  return (byte)PTR_DAT_00653890[(int)param_1 * 2] & 8;
}
