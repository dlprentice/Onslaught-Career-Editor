/* address: 0x004cdba0 */
/* name: CParticleManager__Helper_004cdba0 */
/* signature: void __thiscall CParticleManager__Helper_004cdba0(void * this, int param_1, int param_2) */


void __thiscall CParticleManager__Helper_004cdba0(void *this,int param_1,int param_2)

{
  if (*(int *)((int)this + 8) == 0) {
    *(int *)((int)this + 8) = param_1;
    *(int *)((int)this + 4) = param_1;
    *(undefined4 *)(param_1 + 0x3c) = 0;
    *(undefined4 *)(param_1 + 0x40) = 0;
    return;
  }
  *(int *)(*(int *)((int)this + 8) + 0x40) = param_1;
  *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)((int)this + 8);
  *(int *)((int)this + 8) = param_1;
  return;
}
