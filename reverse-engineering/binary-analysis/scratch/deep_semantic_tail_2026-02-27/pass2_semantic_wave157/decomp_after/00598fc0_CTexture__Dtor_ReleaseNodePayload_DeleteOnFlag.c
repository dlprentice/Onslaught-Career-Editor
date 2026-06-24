/* address: 0x00598fc0 */
/* name: CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag */
/* signature: void * __thiscall CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void * this, void * param_1, int param_2) */


void * __thiscall
CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void *this,void *param_1,int param_2)

{
  CTexture__Helper_00598e22(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
