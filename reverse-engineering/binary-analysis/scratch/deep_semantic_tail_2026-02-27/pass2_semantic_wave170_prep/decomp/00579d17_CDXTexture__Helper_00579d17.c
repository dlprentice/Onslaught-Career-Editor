/* address: 0x00579d17 */
/* name: CDXTexture__Helper_00579d17 */
/* signature: void * __thiscall CDXTexture__Helper_00579d17(void * this, void * param_1, int param_2) */


void * __thiscall CDXTexture__Helper_00579d17(void *this,void *param_1,int param_2)

{
  CDXTexture__Helper_00579cbe((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
