/* address: 0x0056a106 */
/* name: CTexture__Unk_0056a106 */
/* signature: uint __thiscall CTexture__Unk_0056a106(void * this, void * param_1, int param_2) */


uint __thiscall CTexture__Unk_0056a106(void *this,void *param_1,int param_2)

{
  uint uVar1;
  uint unaff_retaddr;

  if (1 < DAT_00653a9c) {
    uVar1 = CTexture__Helper_00563951(this,(int)param_1,0x107,unaff_retaddr);
    return uVar1;
  }
  return *(ushort *)(PTR_DAT_00653890 + (int)param_1 * 2) & 0x107;
}
