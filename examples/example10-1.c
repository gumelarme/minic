int result;
int power(int n){
  if(n==0){
    return 1;
  } else{
    return power(n-1);
  }
}

void main(void){
  result = power(5 * 2*(1 + 2));
}
