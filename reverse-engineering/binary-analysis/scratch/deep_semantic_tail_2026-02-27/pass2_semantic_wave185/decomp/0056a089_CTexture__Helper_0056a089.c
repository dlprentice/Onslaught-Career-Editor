/* address: 0x0056a089 */
/* name: CTexture__Helper_0056a089 */
/* signature: uint __thiscall CTexture__Helper_0056a089(void * this, void * param_1, int param_2) */


uint __thiscall CTexture__Helper_0056a089(void *this,void *param_1,int param_2)

{
  uint uVar1;
  uint unaff_retaddr;

  if (1 < DAT_00653a9c) {
    uVar1 = CRT__GetCharTypeMask_Compat(this,(int)param_1,4,unaff_retaddr);
    return uVar1;
  }
  return (byte)PTR_DAT_00653890[(int)param_1 * 2] & 4;
}
