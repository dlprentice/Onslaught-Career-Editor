/* address: 0x004ec250 */
/* name: CStaticShadows__Unk_004ec250 */
/* signature: void * __thiscall CStaticShadows__Unk_004ec250(void * this, void * param_1, int param_2) */


void * __thiscall CStaticShadows__Unk_004ec250(void *this,void *param_1,int param_2)

{
  int iVar1;

  if (((uint)param_1 & 2) != 0) {
    CDXLandscape__Helper_0055db0a
              ((int)this,0x1c,*(int *)((int)this + -4),CStaticShadows__Destructor);
    if (((uint)param_1 & 1) != 0) {
      OID__FreeObject((void *)((int)this + -4));
    }
    return (void *)((int)this + -4);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    iVar1 = 0;
    if (0 < *(int *)((int)this + 0xc) * *(int *)((int)this + 8)) {
      do {
        OID__FreeObject(*(void **)(*(int *)((int)this + 0x10) + iVar1 * 4));
        iVar1 = iVar1 + 1;
      } while (iVar1 < *(int *)((int)this + 0xc) * *(int *)((int)this + 8));
    }
    OID__FreeObject(*(void **)((int)this + 0x10));
  }
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
