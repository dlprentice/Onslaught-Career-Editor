/* address: 0x004cd7a0 */
/* name: CWorldPhysicsManager__FindNodeByNameGE */
/* signature: void * __thiscall CWorldPhysicsManager__FindNodeByNameGE(void * this, void * node_name, void * unused_ctx) */


void * __thiscall
CWorldPhysicsManager__FindNodeByNameGE(void *this,void *node_name,void *unused_ctx)

{
  void *pvVar1;
  int iVar2;

  pvVar1 = *(void **)this;
  DAT_0082b3f8 = this;
  while( true ) {
    if (pvVar1 == (void *)0x0) {
      return (void *)0x0;
    }
    iVar2 = stricmp(node_name,(char *)((int)pvVar1 + 4));
    if (iVar2 == 0) break;
    if (iVar2 < 0) {
      return (void *)0x0;
    }
    DAT_0082b3f8 = (int *)((int)pvVar1 + 0x38);
    pvVar1 = (void *)*DAT_0082b3f8;
  }
  return pvVar1;
}
