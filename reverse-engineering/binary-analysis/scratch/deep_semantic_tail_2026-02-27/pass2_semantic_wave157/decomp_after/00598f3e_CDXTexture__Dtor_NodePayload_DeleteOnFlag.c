/* address: 0x00598f3e */
/* name: CDXTexture__Dtor_NodePayload_DeleteOnFlag */
/* signature: int __thiscall CDXTexture__Dtor_NodePayload_DeleteOnFlag(void * this, void * param_1, int param_2) */


int __thiscall CDXTexture__Dtor_NodePayload_DeleteOnFlag(void *this,void *param_1,int param_2)

{
  *(undefined ***)this = &PTR_CDXTexture__Dtor_NodePayload_DeleteOnFlag_005ef230;
  CFastVB__Helper_0059871c(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return (int)this;
}
