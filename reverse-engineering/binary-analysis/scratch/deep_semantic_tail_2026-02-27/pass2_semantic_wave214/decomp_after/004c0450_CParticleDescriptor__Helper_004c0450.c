/* address: 0x004c0450 */
/* name: CParticleDescriptor__Helper_004c0450 */
/* signature: void __thiscall CParticleDescriptor__Helper_004c0450(void * this, int param_1, void * param_2) */


void __thiscall CParticleDescriptor__Helper_004c0450(void *this,int param_1,void *param_2)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;

  iVar1 = *(int *)((int)this + 4);
  if (iVar1 != 0) {
    puVar3 = (undefined4 *)(iVar1 + 0x10);
    for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar3 = *(undefined4 *)param_1;
      param_1 = (int)(param_1 + 4);
      puVar3 = puVar3 + 1;
    }
    *(undefined4 *)(iVar1 + 0xa0) = 1;
  }
  return;
}
