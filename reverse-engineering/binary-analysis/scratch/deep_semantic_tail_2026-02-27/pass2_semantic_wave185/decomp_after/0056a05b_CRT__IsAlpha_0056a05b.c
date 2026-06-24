/* address: 0x0056a05b */
/* name: CRT__IsAlpha_0056a05b */
/* signature: uint __thiscall CRT__IsAlpha_0056a05b(void * this, void * param_1, int param_2) */


uint __thiscall CRT__IsAlpha_0056a05b(void *this,void *param_1,int param_2)

{
  uint uVar1;
  uint unaff_retaddr;

  if (1 < DAT_00653a9c) {
    uVar1 = CRT__GetCharTypeMask_Compat(this,(int)param_1,0x103,unaff_retaddr);
    return uVar1;
  }
  return *(ushort *)(PTR_DAT_00653890 + (int)param_1 * 2) & 0x103;
}
