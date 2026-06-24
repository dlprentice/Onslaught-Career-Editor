/* address: 0x004c0510 */
/* name: CParticleManager__LinkNodeFront */
/* signature: void __thiscall CParticleManager__LinkNodeFront(void * this, void * node, void * context) */


void __thiscall CParticleManager__LinkNodeFront(void *this,void *node,void *context)

{
  int unaff_ESI;

  if (*(int *)((int)this + 0x54) == 0) {
    CParticleManager__LinkNodeByOffset3C40(&DAT_0082b400,(int)this,unaff_ESI);
    *(void **)((int)this + 0x50) = node;
    *(void **)((int)this + 0x54) = node;
    *(undefined4 *)node = 0;
    *(undefined4 *)((int)node + 4) = 0;
    return;
  }
  *(void **)(*(int *)((int)this + 0x50) + 4) = node;
  *(undefined4 *)node = *(undefined4 *)((int)this + 0x50);
  *(void **)((int)this + 0x50) = node;
  return;
}
