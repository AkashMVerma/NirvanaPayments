/*
  Nirvana Construction
*/

#include <pbc/pbc.h>
#include <pbc/pbc_test.h>

int main(int argc, char **argv) {
  pairing_t pairing;
  double ti0, ti1, ttotal, ttotalReg, ttotalSpe, ttotalVer, ttotalDec;
  element_t mes, ID, W, y, y2, y3, g, h, pk1, pk2, pp, C, C1, c1, C2, c2, sec, sec1, sec2, pair, z, r, u, x, v, V, X, R, S, T, t , t1, t2, t3, t4, t5;
  
  pbc_demo_pairing_init(pairing, argc, argv);

  element_init_Zr(y, pairing);
  element_init_Zr(y2, pairing);
  element_init_Zr(y3, pairing);
  element_init_G1(g, pairing);
  element_init_G2(h, pairing);
  element_init_GT(pair, pairing);
  element_init_Zr(sec, pairing);
  element_init_Zr(sec1, pairing);
  element_init_Zr(sec2, pairing);
  element_init_G2(pk1, pairing);
  element_init_G2(pk2, pairing);
  element_init_G2(pp, pairing);
  element_init_Zr(v, pairing);
  element_init_G2(V, pairing);
  element_init_G1(X, pairing);
  element_init_G1(W, pairing);
  element_init_G2(R, pairing);
  element_init_G1(S, pairing);
  element_init_G1(T, pairing);
  element_init_Zr(t, pairing);
  element_init_GT(ID, pairing);
  element_init_GT(mes, pairing);
  element_init_Zr(x, pairing);
  element_init_G1(r, pairing);
  element_init_GT(C, pairing);
  element_init_GT(C2, pairing);
  element_init_GT(C1, pairing);
  element_init_GT(z, pairing);
  element_init_GT(t1, pairing);
  element_init_GT(t2, pairing);
  element_init_GT(t3, pairing);
  element_init_GT(t4, pairing);
  element_init_GT(t5, pairing);


  ttotal = 0.0;
  ttotalReg = 0.0;
  ttotalSpe = 0.0;
  ttotalVer = 0.0;
  ttotalVer == 0.0;

  //Setup:
  element_random(g);
  element_random(h);
  element_random(sec);
  element_pairing(pair, g, h);
  element_pow_zn(pp, h, sec);
  //mpk={g,h,pair,pp}
  //msk={sec}
  
  element_printf("Size of elements in Z = %d\n", element_length_in_bytes(sec));
  element_printf("Size of elements in G_1 = %d\n", element_length_in_bytes(g));
  element_printf("Size of elements in G_2 = %d\n", element_length_in_bytes(h));
  element_printf("Size of elements in G_t = %d\n", element_length_in_bytes(pair));
  
  //KeyGen:
  element_random(sec1);
  element_sub(sec2, sec, sec1);
  element_pow_zn(pk1, h, sec1);
  element_pow_zn(pk2, h, sec2);
  //pk={pk1,pk2}
  //sk={sec1,sec2}
  
  element_random(v);
  element_pow_zn(V, h, v);
  //Sgk={v}
  //vk={V}

  ti0 = pbc_get_time();
  //Registeration
  element_random(x);
  element_invert(x,x);
  element_pow_zn(r,g,x);
  element_random(t);
  element_pow_zn(R, h, t);
  element_invert(t,t);
  element_pow_zn(W,g,t);
  element_mul(v,v,t);
  element_pow2_zn(S, r, v, X, t);
  element_pow2_zn(T, S, v, g, t);
  //Signature=(R,S,T)
  ti1 = pbc_get_time();
  ttotalReg=ti1-ti0;

  ti0 = pbc_get_time();
  //Spending:
  element_from_hash(ID, "Mahdi", 5);
  element_pairing(C, r, pp);
  element_mul(C,C,ID);
  element_pairing(C1, r, pk1);
  //CT=(C,C1)
  //Sig_update:
  element_random(y);
  element_pow_zn(S, S, y);
  element_mul(y2, y, y);
  element_sub(y3, y, y2);
  element_pow2_zn(T, T, y2, W, y3);
  element_invert(y,y);
  element_pow_zn(R, R, x);
  ti1 = pbc_get_time();
  ttotalSpe=ti1-ti0;

  ti0 = pbc_get_time();
  //Verification:
  element_pairing(t1,S,R);
  element_pairing(t2,r,V);
  element_pairing(t3,X,h);
  element_mul(t3,t2,t3);
  element_pairing(t4,T,R);
  element_pairing(t5,S,V);
  element_mul(t5,t5,pair);
  
  if (!element_cmp(t1, t3) && !element_cmp(t4, t5)) {
    printf("The collateral is valid\n");
  } else {
    printf("*BUG* The collateral is invalid *BUG*\n");
  }

  ti1 = pbc_get_time();
  ttotalVer=ti1-ti0;

  //Double_Spending:
  element_from_hash(ID, "Mahdi", 5);
  element_pow_zn(r,g,x);
  element_pairing(C, r, pp);
  element_mul(C,C,ID);
  element_pairing(C2, r, pk2);
  //CT'=(C,C2)

  ti0 = pbc_get_time();
  //Decryption:
  element_mul(z,C1,C2);
  element_invert(z,z);
  element_mul(mes,C,z);

  ti1 = pbc_get_time();
  ttotalDec=ti1-ti0;

   if (!element_cmp(ID, mes)) {
    element_printf("Identity of malicious customer is %d\n",mes);
  } else {
    printf("*BUG* The message is wrong *BUG*\n");
  }

  printf("Registeration time = %f\n", ttotalReg);
  printf("Spending time = %f\n", ttotalSpe);
  printf("Verification time = %f\n", ttotalVer);
  printf("Decryption time = %f\n", ttotalDec);
  
  return 0;
}
