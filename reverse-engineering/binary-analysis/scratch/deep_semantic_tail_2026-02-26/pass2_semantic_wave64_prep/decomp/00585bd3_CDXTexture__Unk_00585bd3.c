/* address: 0x00585bd3 */
/* name: CDXTexture__Unk_00585bd3 */
/* signature: void * __thiscall CDXTexture__Unk_00585bd3(void * this, void * param_1, int param_2) */


void * __thiscall CDXTexture__Unk_00585bd3(void *this,void *param_1,int param_2)

{
  CFastVB__Helper_00581263(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
