/* address: 0x00404860 */
/* name: CAtmospheric__Unk_00404860 */
/* signature: int __thiscall CAtmospheric__Unk_00404860(void * this, int param_1, int param_2, int param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall
CAtmospheric__Unk_00404860(void *this,int param_1,int param_2,int param_3,int param_4)

{
  double dVar1;
  int unaff_EDI;
  double dVar2;

  if ((param_1 != *(int *)((int)this + 0x14)) || (param_2 != 0)) {
    *(int *)((int)this + 0x1c) = param_3;
    dVar2 = CAtmospheric__Helper_004f3c80
                      (*(void **)((int)this + 0x20),param_1,(int)this + 0x10,unaff_EDI);
    if (param_2 != 0) {
      *(undefined4 *)((int)this + 8) = 0;
    }
    *(float *)((int)this + 0x18) = (float)dVar2;
    dVar1 = _DAT_005d87d8;
    *(int *)((int)this + 0x14) = param_1;
    if (dVar2 <= dVar1) {
      *(undefined4 *)((int)this + 0x18) = 0x3f800000;
    }
  }
  return 1;
}
