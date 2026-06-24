/* address: 0x00598f22 */
/* name: CDXTexture__Unk_00598f22 */
/* signature: void * __thiscall CDXTexture__Unk_00598f22(void * this, void * param_1, int param_2) */


void * __thiscall CDXTexture__Unk_00598f22(void *this,void *param_1,int param_2)

{
  CFastVB__Helper_0059871c(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
