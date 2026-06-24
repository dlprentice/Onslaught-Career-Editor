/* address: 0x0040c720 */
/* name: CGeneralVolume__ResetAndSetActiveReader */
/* signature: void __thiscall CGeneralVolume__ResetAndSetActiveReader(void * this, int param_1, void * param_2) */


void __thiscall CGeneralVolume__ResetAndSetActiveReader(void *this,int param_1,void *param_2)

{
  CBattleEngine__Unk_00406460((int)this);
  CGenericActiveReader__SetReader((void *)((int)this + 0x264),(void *)param_1);
  CGeneralVolume__Helper_00402020((int)this);
  return;
}
