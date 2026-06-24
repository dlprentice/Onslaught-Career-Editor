/* address: 0x004cd7a0 */
/* name: CWorldPhysicsManager__Helper_004cd7a0 */
/* signature: int __thiscall CWorldPhysicsManager__Helper_004cd7a0(void * this, void * param_1, void * param_2) */


int __thiscall CWorldPhysicsManager__Helper_004cd7a0(void *this,void *param_1,void *param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = *(int *)this;
  DAT_0082b3f8 = this;
  while( true ) {
    if (iVar1 == 0) {
      return 0;
    }
    iVar2 = stricmp(param_1,(char *)(iVar1 + 4));
    if (iVar2 == 0) break;
    if (iVar2 < 0) {
      return 0;
    }
    DAT_0082b3f8 = (int *)(iVar1 + 0x38);
    iVar1 = *DAT_0082b3f8;
  }
  return iVar1;
}
