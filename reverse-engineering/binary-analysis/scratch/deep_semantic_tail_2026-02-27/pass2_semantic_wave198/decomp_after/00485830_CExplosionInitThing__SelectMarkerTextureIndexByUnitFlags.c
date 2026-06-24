/* address: 0x00485830 */
/* name: CExplosionInitThing__SelectMarkerTextureIndexByUnitFlags */
/* signature: int __thiscall CExplosionInitThing__SelectMarkerTextureIndexByUnitFlags(void * this, int param_1, int param_2) */


int __thiscall
CExplosionInitThing__SelectMarkerTextureIndexByUnitFlags(void *this,int param_1,int param_2)

{
  uint uVar1;
  int iVar2;

  uVar1 = *(uint *)(param_1 + 0x34);
  if ((uVar1 & 0x8000000) == 0) {
    if (((uVar1 & 0x10) != 0) && (iVar2 = *(int *)(param_1 + 0x164), iVar2 != 0)) {
      if (*(int *)(iVar2 + 0x124) != 0) goto switchD_00485875_caseD_9;
      if (iVar2 != 0) {
        switch(*(undefined4 *)(iVar2 + 0xe0)) {
        case 9:
        case 0x11:
        case 0x15:
        case 0x17:
          goto switchD_00485875_caseD_9;
        }
      }
    }
    if ((uVar1 & 0x4000) != 0) {
      return *(int *)((int)this + 0x1a0);
    }
    if (((uVar1 & 0x4008100) == 0) && ((uVar1 & 0x40) == 0)) {
      return *(int *)((int)this + 0x1a4);
    }
  }
switchD_00485875_caseD_9:
  return *(int *)((int)this + 0x1a8);
}
