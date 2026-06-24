/* address: 0x004c0510 */
/* name: CParticleManager__LinkNodeFront */
/* signature: void __thiscall CParticleManager__LinkNodeFront(void * this, int param_1, void * param_2) */


void __thiscall CParticleManager__LinkNodeFront(void *this,int param_1,void *param_2)

{
  int unaff_ESI;

  if (*(int *)((int)this + 0x54) == 0) {
    CParticleManager__LinkNodeByOffset3C40(&DAT_0082b400,(int)this,unaff_ESI);
    *(int *)((int)this + 0x50) = param_1;
    *(int *)((int)this + 0x54) = param_1;
    *(undefined4 *)param_1 = 0;
    *(undefined4 *)(param_1 + 4) = 0;
    return;
  }
  *(int *)(*(int *)((int)this + 0x50) + 4) = param_1;
  *(undefined4 *)param_1 = *(undefined4 *)((int)this + 0x50);
  *(int *)((int)this + 0x50) = param_1;
  return;
}
