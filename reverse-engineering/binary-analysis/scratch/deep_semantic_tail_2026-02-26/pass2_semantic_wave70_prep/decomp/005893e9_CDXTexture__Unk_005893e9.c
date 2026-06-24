/* address: 0x005893e9 */
/* name: CDXTexture__Unk_005893e9 */
/* signature: void * __thiscall CDXTexture__Unk_005893e9(void * this, void * param_1, int param_2) */


void * __thiscall CDXTexture__Unk_005893e9(void *this,void *param_1,int param_2)

{
  CDXTexture__Unk_005893d1((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
