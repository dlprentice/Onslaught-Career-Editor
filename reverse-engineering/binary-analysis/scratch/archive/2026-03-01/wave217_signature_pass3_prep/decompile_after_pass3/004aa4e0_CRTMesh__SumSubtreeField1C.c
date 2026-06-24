/* address: 0x004aa4e0 */
/* name: CRTMesh__SumSubtreeField1C */
/* signature: int __thiscall CRTMesh__SumSubtreeField1C(void * this) */


int __thiscall CRTMesh__SumSubtreeField1C(void *this)

{
  int iVar1;

  if (*(void **)((int)this + 8) != (void *)0x0) {
    iVar1 = CRTMesh__SumSubtreeField1C(*(void **)((int)this + 8));
    return iVar1 + *(int *)((int)this + 0x1c);
  }
  return *(int *)((int)this + 0x1c);
}
