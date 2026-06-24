/* address: 0x004cdba0 */
/* name: CParticleManager__LinkNodeByOffset3C40 */
/* signature: void __thiscall CParticleManager__LinkNodeByOffset3C40(void * this, void * node, int unused_ctx) */


void __thiscall CParticleManager__LinkNodeByOffset3C40(void *this,void *node,int unused_ctx)

{
  if (*(int *)((int)this + 8) == 0) {
    *(void **)((int)this + 8) = node;
    *(void **)((int)this + 4) = node;
    *(undefined4 *)((int)node + 0x3c) = 0;
    *(undefined4 *)((int)node + 0x40) = 0;
    return;
  }
  *(void **)(*(int *)((int)this + 8) + 0x40) = node;
  *(undefined4 *)((int)node + 0x3c) = *(undefined4 *)((int)this + 8);
  *(void **)((int)this + 8) = node;
  return;
}
