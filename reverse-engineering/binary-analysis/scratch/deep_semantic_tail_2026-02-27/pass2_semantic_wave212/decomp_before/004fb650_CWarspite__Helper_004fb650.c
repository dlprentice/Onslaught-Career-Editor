/* address: 0x004fb650 */
/* name: CWarspite__Helper_004fb650 */
/* signature: void __thiscall CWarspite__Helper_004fb650(void * this, int param_1, int param_2, int param_3) */


void __thiscall CWarspite__Helper_004fb650(void *this,int param_1,int param_2,int param_3)

{
  void *unaff_retaddr;

  if (*(void **)((int)this + 0x140) != (void *)0x0) {
    OID__UpdateAimTransformAndAttachTargetReader
              (*(void **)((int)this + 0x140),(void *)param_1,(void *)param_2,unaff_retaddr);
  }
  return;
}
