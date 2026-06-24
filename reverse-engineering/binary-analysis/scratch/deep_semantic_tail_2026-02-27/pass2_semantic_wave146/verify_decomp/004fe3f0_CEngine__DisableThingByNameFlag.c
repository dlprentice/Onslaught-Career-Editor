/* address: 0x004fe3f0 */
/* name: CEngine__DisableThingByNameFlag */
/* signature: void __thiscall CEngine__DisableThingByNameFlag(void * this, int param_1, void * param_2) */


void __thiscall CEngine__DisableThingByNameFlag(void *this,int param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  int unaff_EDI;
  int *piVar3;

  piVar3 = *(int **)((int)this + 0x18c);
  if (piVar3 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar3;
  }
  if (iVar2 != 0) {
    while (iVar1 = stricmp((char *)param_1,*(char **)(*(int *)(iVar2 + 0x3d0) + 8)), iVar1 != 0) {
      piVar3 = (int *)piVar3[1];
      if (piVar3 == (int *)0x0) {
        iVar2 = 0;
      }
      else {
        iVar2 = *piVar3;
      }
      if (iVar2 == 0) {
        return;
      }
    }
    *(undefined4 *)(iVar2 + 0x3f4) = 0;
    if (*(int *)((int)this + 0x144) == iVar2) {
      CGenericActiveReader__SetReader((int *)((int)this + 0x144),(void *)0x0);
    }
    if (*(void **)((int)this + 0x13c) != (void *)0x0) {
      CSquadNormal__Helper_004ffdd0(*(void **)((int)this + 0x13c),0,(void *)0x0,unaff_EDI);
    }
  }
  return;
}
