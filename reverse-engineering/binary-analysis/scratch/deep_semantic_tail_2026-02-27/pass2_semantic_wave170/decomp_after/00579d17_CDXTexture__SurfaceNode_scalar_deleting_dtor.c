/* address: 0x00579d17 */
/* name: CDXTexture__SurfaceNode_scalar_deleting_dtor */
/* signature: void * __thiscall CDXTexture__SurfaceNode_scalar_deleting_dtor(void * this, void * param_1, int param_2) */


void * __thiscall CDXTexture__SurfaceNode_scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  CDXTexture__FreeSurfaceNodeTree((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
