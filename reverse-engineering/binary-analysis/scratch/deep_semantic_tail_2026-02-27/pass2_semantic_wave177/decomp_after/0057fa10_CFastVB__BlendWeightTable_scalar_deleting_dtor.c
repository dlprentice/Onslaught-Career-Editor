/* address: 0x0057fa10 */
/* name: CFastVB__BlendWeightTable_scalar_deleting_dtor */
/* signature: int * __thiscall CFastVB__BlendWeightTable_scalar_deleting_dtor(void * this, void * param_1, int param_2) */


int * __thiscall
CFastVB__BlendWeightTable_scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  int *ptr;

  if (((uint)param_1 & 2) == 0) {
    OID__FreeObject_Callback(*(void **)this);
    ptr = this;
    if (((uint)param_1 & 1) != 0) {
      OID__FreeObject_Callback(this);
    }
  }
  else {
    ptr = (int *)((int)this + -4);
    CDXTexture__RepeatCallbackN((int)this,0xc,*ptr,&LAB_0057cc9b);
    if (((uint)param_1 & 1) != 0) {
      OID__FreeObject_Callback(ptr);
    }
  }
  return ptr;
}
