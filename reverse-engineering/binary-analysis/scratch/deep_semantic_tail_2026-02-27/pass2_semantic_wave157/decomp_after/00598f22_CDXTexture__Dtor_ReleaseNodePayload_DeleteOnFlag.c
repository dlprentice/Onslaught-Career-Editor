/* address: 0x00598f22 */
/* name: CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag */
/* signature: void * __thiscall CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void * this, void * param_1, int param_2) */


void * __thiscall
CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void *this,void *param_1,int param_2)

{
  CFastVB__Helper_0059871c(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
